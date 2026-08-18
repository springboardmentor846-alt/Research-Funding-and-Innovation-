"""Commercialization Recommendations service.

Takes the per-patent innovation scores and the technology trends and
assigns each patent a *commercialization label* explaining the
business opportunity the patent represents.  Labels are derived from
purely computed signals — no hardcoded recommendations.

Label rules
-----------

The rule engine evaluates the patent's innovation score, technology
growth rate, the patent density in its area, the citation trend, and
its age.  Labels are mutually-exclusive and applied in priority
order:

1. ``High Commercial Potential`` — high innovation score AND
   fast-growing technology area.
2. ``Strong Licensing Opportunity`` — high citation impact,
   mid-or-higher innovation score.
3. ``Highly Competitive Technology`` — high patent density in the
   area (a hot field) but a mid-or-lower innovation score.
4. ``Emerging Technology`` — emerging flag set on the technology
   trend AND mid-or-higher innovation score.
5. ``Consider Patent Filing`` — low patent density AND a recent
   filing year (room to claim space in the area).

If none of the above match, the patent receives no label (the
dashboard simply omits it from the recommendations list).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.patent import InnovationScore, Patent, TechnologyTrend


HIGH_COMMERCIAL_THRESHOLD = 0.65
GOOD_COMMERCIAL_THRESHOLD = 0.50
COMPETITIVE_DENSITY_THRESHOLD = 0.18  # share of corpus
RECENT_YEAR_WINDOW = 3
HIGH_CITATION_THRESHOLD = 15  # absolute citations


class CommercializationService:
    """Stateless service for commercialization recommendations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def compute_for_all(self) -> Dict[str, Any]:
        """Label every patent with a commercialization label and reason."""
        patents = (
            self.db.query(Patent)
            .filter(Patent.publication_year.isnot(None))
            .all()
        )
        if not patents:
            return {"labelled": 0, "by_label": {}}

        by_tech_share = self._technology_shares(patents)
        latest_year = self._latest_year(patents)
        tech_growth = self._technology_recent_growth(latest_year)
        tech_emerging = self._technology_emerging_flags(latest_year)
        scores = {
            s.patent_id: s
            for s in self.db.query(InnovationScore).all()
        }
        summary: Dict[str, int] = {}
        labelled = 0
        for p in patents:
            score = scores.get(p.id)
            final = float(score.final_score) if score else 0.0
            growth = tech_growth.get(p.technology_area or "", 0.0)
            density = by_tech_share.get(p.technology_area or "", 0.0)
            label, reason = self._label_patent(
                p,
                final=final,
                growth=growth,
                density=density,
                tech_emerging=tech_emerging.get(p.technology_area or "", False),
                latest_year=latest_year,
            )
            if label is None:
                continue
            if score is None:
                # Materialise a row so the dashboard reads from the DB.
                score = InnovationScore(patent_id=p.id)
                self.db.add(score)
            score.commercialization_label = label
            score.commercialization_reason = reason
            summary[label] = summary.get(label, 0) + 1
            labelled += 1
        self.db.commit()
        return {"labelled": labelled, "by_label": summary}

    def top_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(InnovationScore)
            .filter(InnovationScore.commercialization_label.isnot(None))
            .order_by(InnovationScore.final_score.desc())
            .limit(limit)
            .all()
        )
        out: List[Dict[str, Any]] = []
        for r in rows:
            patent = self.db.query(Patent).filter(Patent.id == r.patent_id).one_or_none()
            if patent is None:
                continue
            out.append(self._recommendation_to_dict(patent, r))
        return out

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _technology_shares(self, patents: List[Patent]) -> Dict[str, float]:
        total = len(patents) or 1
        counter: Dict[str, int] = {}
        for p in patents:
            key = p.technology_area or "Unclassified"
            counter[key] = counter.get(key, 0) + 1
        return {k: v / total for k, v in counter.items()}

    def _latest_year(self, patents: List[Patent]) -> int:
        years = [p.publication_year for p in patents if p.publication_year]
        return max(years) if years else datetime.utcnow().year

    def _technology_recent_growth(self, latest_year: int) -> Dict[str, float]:
        rows = (
            self.db.query(TechnologyTrend)
            .filter(TechnologyTrend.publication_year == latest_year)
            .all()
        )
        return {r.technology_area: float(r.growth_rate or 0.0) for r in rows}

    def _technology_emerging_flags(self, latest_year: int) -> Dict[str, bool]:
        rows = (
            self.db.query(TechnologyTrend)
            .filter(TechnologyTrend.is_emerging.is_(True))
            .filter(TechnologyTrend.publication_year >= latest_year - 1)
            .all()
        )
        return {r.technology_area: True for r in rows}

    def _label_patent(
        self,
        patent: Patent,
        *,
        final: float,
        growth: float,
        density: float,
        tech_emerging: bool,
        latest_year: int,
    ) -> (Optional[str], Optional[str]):
        # 1. High commercial potential
        if final >= HIGH_COMMERCIAL_THRESHOLD and growth >= 0.5:
            return (
                "High Commercial Potential",
                (
                    f"Innovation score {round(final, 2)} with technology growth "
                    f"rate {round(growth, 2)}; indicates a fast-moving area with "
                    "strong patent quality."
                ),
            )
        # 2. Strong licensing opportunity
        if (patent.citations or 0) >= HIGH_CITATION_THRESHOLD and final >= GOOD_COMMERCIAL_THRESHOLD:
            return (
                "Strong Licensing Opportunity",
                (
                    f"High citation impact ({patent.citations}) and innovation "
                    f"score {round(final, 2)}; the patent is well-positioned for "
                    "licensing negotiations."
                ),
            )
        # 3. Highly competitive technology
        if density >= COMPETITIVE_DENSITY_THRESHOLD and final < GOOD_COMMERCIAL_THRESHOLD:
            return (
                "Highly Competitive Technology",
                (
                    f"Technology area represents {round(density * 100, 1)}% of the "
                    f"corpus; expect crowded IP space."
                ),
            )
        # 4. Emerging technology
        if tech_emerging and final >= GOOD_COMMERCIAL_THRESHOLD:
            return (
                "Emerging Technology",
                (
                    f"Technology area is flagged emerging in {patent.publication_year}; "
                    f"innovation score {round(final, 2)} supports early-mover "
                    "opportunities."
                ),
            )
        # 5. Consider patent filing
        age = latest_year - (patent.publication_year or latest_year)
        if density < 0.08 and age <= RECENT_YEAR_WINDOW and final >= 0.3:
            return (
                "Consider Patent Filing",
                (
                    f"Low patent density ({round(density * 100, 1)}%) in this "
                    f"area and a recent filing year {patent.publication_year}; "
                    "suggests an under-claimed space."
                ),
            )
        return None, None

    def _recommendation_to_dict(
        self, patent: Patent, score: InnovationScore
    ) -> Dict[str, Any]:
        return {
            "patent_id": patent.id,
            "patent_number": patent.patent_number,
            "title": patent.title,
            "assignee": patent.assignee,
            "source": patent.source,
            "publication_year": patent.publication_year,
            "technology_area": patent.technology_area,
            "citations": patent.citations,
            "innovation_score": float(score.final_score),
            "commercialization_label": score.commercialization_label,
            "commercialization_reason": score.commercialization_reason,
        }
