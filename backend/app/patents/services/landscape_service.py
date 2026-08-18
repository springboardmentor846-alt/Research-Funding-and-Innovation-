"""Patent Landscape Analysis service.

Computes the *Patent Landscape Analysis* tile of the analytics
dashboard.  Every value is derived from the live ``patents`` table —
no hardcoded numbers, no mock data.

Outputs match ``PatentAnalyticsOverview`` (see ``app.schemas.patent``):

* ``total_patents``
* ``total_citations``
* ``by_source`` / ``by_technology`` / ``by_year`` / ``by_country``
* ``top_assignees`` / ``top_inventors``
* ``citation_stats`` — total, average, max, highly-cited count
* ``growth_trend`` — year-over-year counts and growth rates
* ``most_active_organizations`` — same as ``top_assignees``
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.patent import Patent


HIGHLY_CITED_THRESHOLD = 10  # citations >= this counts as "highly cited"


def _row_to_dict(row) -> Dict[str, Any]:
    return {col: getattr(row, col) for col in row._fields}


def _safe_div(a: float, b: float) -> Optional[float]:
    if not b:
        return None
    return round(a / b, 4)


class PatentLandscapeService:
    """Stateless service that produces the landscape analytics payload."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def overview(self) -> Dict[str, Any]:
        return {
            "total_patents": self._total_patents(),
            "total_citations": self._total_citations(),
            "by_source": self.by_source(),
            "by_technology": self.by_technology(),
            "by_year": self.by_year(),
            "by_country": self.by_country(),
            "top_assignees": self.top_assignees(),
            "top_inventors": self.top_inventors(),
            "citation_stats": self.citation_stats(),
            "growth_trend": self.growth_trend(),
            "most_active_organizations": self.top_assignees(),
        }

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    def _total_patents(self) -> int:
        return int(self.db.query(func.count(Patent.id)).scalar() or 0)

    def _total_citations(self) -> int:
        return int(self.db.query(func.coalesce(func.sum(Patent.citations), 0)).scalar() or 0)

    def by_source(self) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(Patent.source, func.count(Patent.id))
            .group_by(Patent.source)
            .order_by(func.count(Patent.id).desc())
            .all()
        )
        return [{"source": s, "count": int(c)} for s, c in rows if s]

    def by_technology(self) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(Patent.technology_area, func.count(Patent.id))
            .group_by(Patent.technology_area)
            .order_by(func.count(Patent.id).desc())
            .all()
        )
        return [
            {"technology": t or "Unclassified", "count": int(c)}
            for t, c in rows
        ]

    def by_year(self) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(
                Patent.publication_year,
                func.count(Patent.id),
                func.coalesce(func.sum(Patent.citations), 0),
            )
            .filter(Patent.publication_year.isnot(None))
            .group_by(Patent.publication_year)
            .order_by(Patent.publication_year.asc())
            .all()
        )
        return [
            {"year": int(y), "count": int(c), "citations": int(cites)}
            for y, c, cites in rows
        ]

    def by_country(self) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(Patent.country, func.count(Patent.id))
            .group_by(Patent.country)
            .order_by(func.count(Patent.id).desc())
            .all()
        )
        return [
            {"country": c or "Unknown", "count": int(n)} for c, n in rows
        ]

    def top_assignees(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Top assignees by patent count.

        Uses the legacy ``Patent.assignee`` string column.  When the
        Lens provider has populated the structured ``applicant_names``
        JSON column those entries are merged in (Lens rows often have
        a coarser ``assignee`` so the structured list is more
        accurate).
        """
        rows = (
            self.db.query(
                Patent.assignee,
                func.count(Patent.id),
                func.coalesce(func.sum(Patent.citations), 0),
            )
            .filter(Patent.assignee.isnot(None))
            .group_by(Patent.assignee)
            .order_by(func.count(Patent.id).desc())
            .limit(limit)
            .all()
        )
        counter: Counter = Counter()
        cite_sum: Dict[str, int] = defaultdict(int)
        for a, n, cites in rows:
            if not a:
                continue
            counter[a] += int(n)
            cite_sum[a] += int(cites)

        # Augment with Lens applicant_names JSON when present.  Each
        # row may contribute multiple names; we don't have per-name
        # citation counts at this granularity, so we just bump the
        # count.
        json_rows = (
            self.db.query(Patent.applicant_names)
            .filter(Patent.applicant_names.isnot(None))
            .all()
        )
        for (names,) in json_rows:
            if not names:
                continue
            for name in self._iter_json_strings(names):
                if name:
                    counter[name] += 1

        top = counter.most_common(limit)
        return [
            {
                "assignee": a,
                "count": int(n),
                "total_citations": int(cite_sum.get(a, 0)),
            }
            for a, n in top
        ]

    def top_inventors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Top inventors by appearance count.

        Uses both the legacy comma-separated ``Patent.inventors``
        string AND the structured ``Patent.inventor_names`` JSON list
        populated by the Lens provider.
        """
        counter: Counter = Counter()

        rows = (
            self.db.query(Patent.inventors)
            .filter(Patent.inventors.isnot(None))
            .all()
        )
        for (inventors_str,) in rows:
            if not inventors_str:
                continue
            for name in str(inventors_str).replace(";", ",").split(","):
                name = name.strip()
                if name:
                    counter[name] += 1

        # Lens structured inventor_names (more accurate than the
        # string column when the Lens provider has populated them).
        json_rows = (
            self.db.query(Patent.inventor_names)
            .filter(Patent.inventor_names.isnot(None))
            .all()
        )
        for (names,) in json_rows:
            if not names:
                continue
            for name in self._iter_json_strings(names):
                if name:
                    counter[name] += 1

        return [
            {"inventor": name, "count": int(c)}
            for name, c in counter.most_common(limit)
        ]

    @staticmethod
    def _iter_json_strings(value: Any) -> List[str]:
        """Yield string members from a JSON column that may be a list of
        strings or a list of dicts with a ``name``/``display_name`` key.
        """
        if value is None:
            return []
        if isinstance(value, str):
            # Some drivers serialise JSON to text; try to decode.
            try:
                import json

                value = json.loads(value)
            except Exception:
                return []
        if not isinstance(value, list):
            return []
        out: List[str] = []
        for item in value:
            if isinstance(item, str):
                if item.strip():
                    out.append(item.strip())
            elif isinstance(item, dict):
                name = (
                    item.get("name")
                    or item.get("display_name")
                    or item.get("full_name")
                )
                if isinstance(name, str) and name.strip():
                    out.append(name.strip())
        return out

    def citation_stats(self) -> Dict[str, Any]:
        total = self._total_citations()
        n = self._total_patents()
        if n == 0:
            return {
                "total": 0,
                "average": 0.0,
                "max": 0,
                "highly_cited_count": 0,
            }
        avg = total / n
        max_c = int(self.db.query(func.max(Patent.citations)).scalar() or 0)
        highly = (
            self.db.query(func.count(Patent.id))
            .filter(Patent.citations >= HIGHLY_CITED_THRESHOLD)
            .scalar()
            or 0
        )
        return {
            "total": int(total),
            "average": round(avg, 4),
            "max": int(max_c),
            "highly_cited_count": int(highly),
        }

    def growth_trend(self) -> List[Dict[str, Any]]:
        """Year-over-year growth across all patents."""
        per_year = self.by_year()
        out: List[Dict[str, Any]] = []
        prev_count: Optional[int] = None
        for row in per_year:
            count = row["count"]
            if prev_count is None or prev_count == 0:
                rate: Optional[float] = None
            else:
                rate = round((count - prev_count) / prev_count, 4)
            out.append(
                {
                    "year": row["year"],
                    "count": count,
                    "growth_rate": rate,
                }
            )
            prev_count = count
        return out
