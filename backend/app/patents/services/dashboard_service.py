"""Patent Analytics Dashboard service.

Orchestrates every other service (landscape, technology intel,
innovation scoring, commercialization) into a single payload and
caches it in ``patent_dashboard_cache``.  The dashboard endpoint
serves from cache when present and refreshes when stale.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.patent import InnovationScore, PatentDashboardCache
from app.patents.services.commercialization_service import CommercializationService
from app.patents.services.innovation_scoring_service import InnovationScoringService
from app.patents.services.landscape_service import PatentLandscapeService
from app.patents.services.technology_intel_service import TechnologyIntelligenceService


# Cache TTL in seconds.  The dashboard re-computes when older than this.
CACHE_TTL_SECONDS = 300  # 5 minutes


class PatentDashboardService:
    """Stateless service that produces the analytics dashboard payload."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def get_dashboard(self, *, force_refresh: bool = False) -> Dict[str, Any]:
        cached = self.db.query(PatentDashboardCache).order_by(PatentDashboardCache.id.desc()).first()
        if not force_refresh and cached and self._is_fresh(cached):
            return cached.payload  # type: ignore[return-value]

        payload = self.refresh()
        return payload

    def refresh(self) -> Dict[str, Any]:
        """Run every service and persist the dashboard cache."""
        landscape = PatentLandscapeService(self.db).overview()
        tech = TechnologyIntelligenceService(self.db)
        tech_report = tech.full_report()
        scoring_report = InnovationScoringService(self.db).compute_all()
        commercial_report = CommercializationService(self.db).compute_for_all()
        commercial_recs = CommercializationService(self.db).top_recommendations(limit=10)

        innovation_avg = scoring_report.get("avg_final_score", 0.0)
        total_patents = landscape["total_patents"]
        total_citations = landscape["total_citations"]

        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_patents": total_patents,
            "total_citations": total_citations,
            "innovation_score_avg": innovation_avg,
            "commercialization_summary": commercial_report.get("by_label", {}),
            "analytics": landscape,
            "technology_intelligence": tech_report,
            "recommendations": commercial_recs,
        }

        # Persist as the single-row cache.
        existing = self.db.query(PatentDashboardCache).order_by(PatentDashboardCache.id.desc()).first()
        if existing is None:
            existing = PatentDashboardCache(payload=payload, generated_at=datetime.utcnow())
            self.db.add(existing)
        else:
            existing.payload = payload
            existing.generated_at = datetime.utcnow()
        self.db.commit()

        logger.info(
            f"[patent-dashboard] refreshed; patents={total_patents} "
            f"avg_score={innovation_avg} recs={len(commercial_recs)}"
        )
        return payload

    # ------------------------------------------------------------------
    @staticmethod
    def _is_fresh(cached: PatentDashboardCache) -> bool:
        if not cached.generated_at:
            return False
        age = (datetime.utcnow() - cached.generated_at).total_seconds()
        return age < CACHE_TTL_SECONDS
