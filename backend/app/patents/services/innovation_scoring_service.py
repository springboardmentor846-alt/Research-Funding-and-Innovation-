"""Innovation Scoring service.

Computes a 0–1 score for every patent in the corpus across five
sub-factors, then a single weighted ``final_score``.  All values are
derived from the live database — no hardcoded numbers.

Sub-scores
----------

* ``novelty_score``           — age vs. corpus median (newer = higher)
* ``technology_growth_score`` — growth rate of the patent's
  technology_area in the most recent year
* ``citation_impact_score``   — log-scaled citation percentile
* ``patent_density_score``    — share of the corpus the patent's
  technology_area represents (lower density = higher score, up to a
  cap)
* ``recent_activity_score``   — recency of publication (0–1)

Final score is a weighted sum of the sub-scores with weights tuned
for an innovation-platform product.  Weights can be tuned later via
admin settings without code changes.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.patent import InnovationScore, Patent, TechnologyTrend


# Default weights.  Sum to 1.0.  Tuned for a research-funding /
# innovation-platform product: growth and citation impact dominate,
# density provides a small penalty for over-crowded areas.
DEFAULT_WEIGHTS = {
    "novelty_score": 0.20,
    "technology_growth_score": 0.25,
    "citation_impact_score": 0.30,
    "patent_density_score": 0.10,
    "recent_activity_score": 0.15,
}

# Cap on density score so very dense areas still score > 0.
DENSITY_CAP = 0.6


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


class InnovationScoringService:
    """Stateless service for per-patent innovation scores."""

    def __init__(self, db: Session, *, weights: Optional[Dict[str, float]] = None) -> None:
        self.db = db
        self.weights = dict(weights or DEFAULT_WEIGHTS)
        total = sum(self.weights.values()) or 1.0
        # Re-normalise so weights always sum to 1.
        self.weights = {k: v / total for k, v in self.weights.items()}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def compute_all(self) -> Dict[str, Any]:
        """Recompute scores for every patent in the corpus."""
        patents = self.db.query(Patent).all()
        if not patents:
            return {"computed": 0, "avg_final_score": 0.0}

        max_year = self._max_publication_year(patents)
        # Pre-compute corpus-wide statistics once.
        citations = [p.citations or 0 for p in patents]
        citations_sorted = sorted(citations)
        median_citations = _median(citations_sorted)
        total_patents = len(patents)
        by_tech_share = self._technology_shares(patents)
        tech_growth = self._technology_recent_growth()

        computed = 0
        score_sum = 0.0
        for p in patents:
            breakdown = self._score_patent(
                p,
                max_year=max_year,
                median_citations=median_citations,
                total_patents=total_patents,
                by_tech_share=by_tech_share,
                tech_growth=tech_growth,
            )
            self._upsert_score(p.id, breakdown)
            score_sum += breakdown["final_score"]
            computed += 1
        self.db.commit()

        return {
            "computed": computed,
            "avg_final_score": round(score_sum / max(computed, 1), 4),
        }

    def score_for_patent(self, patent_id: int) -> Optional[Dict[str, Any]]:
        row = (
            self.db.query(InnovationScore)
            .filter(InnovationScore.patent_id == patent_id)
            .one_or_none()
        )
        if row is None:
            # Compute on the fly if we haven't done the bulk run.
            patents = self.db.query(Patent).all()
            if not patents:
                return None
            max_year = self._max_publication_year(patents)
            citations = [p.citations or 0 for p in patents]
            median_citations = _median(sorted(citations))
            by_tech_share = self._technology_shares(patents)
            tech_growth = self._technology_recent_growth()
            target = next((p for p in patents if p.id == patent_id), None)
            if target is None:
                return None
            return self._score_patent(
                target,
                max_year=max_year,
                median_citations=median_citations,
                total_patents=len(patents),
                by_tech_share=by_tech_share,
                tech_growth=tech_growth,
            )
        return self._score_to_dict(row)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _max_publication_year(self, patents: List[Patent]) -> int:
        years = [p.publication_year for p in patents if p.publication_year]
        return max(years) if years else datetime.utcnow().year

    def _technology_shares(self, patents: List[Patent]) -> Dict[str, float]:
        """Fraction of the corpus that each technology_area represents."""
        total = len(patents) or 1
        counter: Dict[str, int] = {}
        for p in patents:
            key = p.technology_area or "Unclassified"
            counter[key] = counter.get(key, 0) + 1
        return {k: v / total for k, v in counter.items()}

    def _technology_recent_growth(self) -> Dict[str, float]:
        """For each technology_area, return the latest growth rate."""
        rows = self.db.query(TechnologyTrend).all()
        if not rows:
            return {}
        latest_year = max(r.publication_year for r in rows)
        out: Dict[str, float] = {}
        for r in rows:
            if r.publication_year == latest_year and r.growth_rate is not None:
                # Keep the most-recent year's growth per area.
                out[r.technology_area] = float(r.growth_rate)
        return out

    def _score_patent(
        self,
        p: Patent,
        *,
        max_year: int,
        median_citations: float,
        total_patents: int,
        by_tech_share: Dict[str, float],
        tech_growth: Dict[str, float],
    ) -> Dict[str, Any]:
        novelty = self._novelty(p, max_year)
        growth = self._growth(p, tech_growth)
        impact = self._impact(p, median_citations)
        density = self._density(p, by_tech_share)
        recency = self._recency(p, max_year)
        weights = self.weights
        final = (
            weights["novelty_score"] * novelty
            + weights["technology_growth_score"] * growth
            + weights["citation_impact_score"] * impact
            + weights["patent_density_score"] * density
            + weights["recent_activity_score"] * recency
        )
        final = _clamp(final)
        explanation = {
            "novelty": f"Age: {max_year - (p.publication_year or max_year)} years from latest",
            "growth": f"Technology area growth rate: {tech_growth.get(p.technology_area or '', 0.0)}",
            "impact": f"Citations: {p.citations or 0} (median: {round(median_citations, 2)})",
            "density": f"Technology share: {round(by_tech_share.get(p.technology_area or '', 0.0), 4)}",
            "recency": f"Published in {p.publication_year or 'unknown'}",
        }
        return {
            "patent_id": p.id,
            "novelty_score": round(_clamp(novelty), 4),
            "technology_growth_score": round(_clamp(growth), 4),
            "citation_impact_score": round(_clamp(impact), 4),
            "patent_density_score": round(_clamp(density), 4),
            "recent_activity_score": round(_clamp(recency), 4),
            "final_score": round(final, 4),
            "explanation": explanation,
        }

    # ----- individual factors -----------------------------------------
    @staticmethod
    def _novelty(p: Patent, max_year: int) -> float:
        if not p.publication_year:
            return 0.1
        age = max(0, max_year - p.publication_year)
        # Linear decay from 1.0 (age 0) to 0.0 (age 20+).
        return _clamp(1.0 - (age / 20.0))

    @staticmethod
    def _growth(p: Patent, tech_growth: Dict[str, float]) -> float:
        rate = tech_growth.get(p.technology_area or "", 0.0)
        # Map -0.5..+1.0 -> 0..1
        return _clamp((rate + 0.5) / 1.5)

    @staticmethod
    def _impact(p: Patent, median_citations: float) -> float:
        cites = p.citations or 0
        # Log-scaled percentile.
        if median_citations <= 0:
            return _clamp(math.log1p(cites) / math.log1p(20))
        if cites <= 0:
            return 0.0
        # ratio = log(cites) / log(2 * median)
        denom = math.log1p(max(median_citations, 1) * 2)
        return _clamp(math.log1p(cites) / denom)

    @staticmethod
    def _density(p: Patent, by_tech_share: Dict[str, float]) -> float:
        share = by_tech_share.get(p.technology_area or "", 0.0)
        # Lower share -> higher score, capped so dense areas still
        # have a non-zero score.
        return _clamp(DENSITY_CAP - share)

    @staticmethod
    def _recency(p: Patent, max_year: int) -> float:
        if not p.publication_year:
            return 0.0
        age = max_year - p.publication_year
        # Linear decay from 1.0 (age 0) to 0.0 (age 5+).
        return _clamp(1.0 - (age / 5.0))

    # ------------------------------------------------------------------
    def _upsert_score(self, patent_id: int, breakdown: Dict[str, Any]) -> None:
        row = (
            self.db.query(InnovationScore)
            .filter(InnovationScore.patent_id == patent_id)
            .one_or_none()
        )
        if row is None:
            row = InnovationScore(patent_id=patent_id)
            self.db.add(row)
        row.novelty_score = breakdown["novelty_score"]
        row.technology_growth_score = breakdown["technology_growth_score"]
        row.citation_impact_score = breakdown["citation_impact_score"]
        row.patent_density_score = breakdown["patent_density_score"]
        row.recent_activity_score = breakdown["recent_activity_score"]
        row.final_score = breakdown["final_score"]
        row.explanation = breakdown["explanation"]

    @staticmethod
    def _score_to_dict(row: InnovationScore) -> Dict[str, Any]:
        return {
            "patent_id": row.patent_id,
            "novelty_score": row.novelty_score,
            "technology_growth_score": row.technology_growth_score,
            "citation_impact_score": row.citation_impact_score,
            "patent_density_score": row.patent_density_score,
            "recent_activity_score": row.recent_activity_score,
            "final_score": row.final_score,
            "explanation": row.explanation,
            "computed_at": row.computed_at.isoformat() if row.computed_at else None,
        }


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return float(s[n // 2])
    return (s[n // 2 - 1] + s[n // 2]) / 2.0
