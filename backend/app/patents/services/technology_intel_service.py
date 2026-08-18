"""Technology Intelligence Engine.

The brain of Milestone 3.  Implements four capabilities:

* **Patent clustering** — K-Means on TF-IDF over (title + abstract +
  keywords) to surface semantically similar patents.  Cluster labels
  are the top TF-IDF tokens of the centroid.  Results are persisted
  in ``patent_clusters`` and the ``patents.cluster_id`` column.
* **Emerging / fast-growing technologies** — recomputed per
  ``(technology_area, publication_year)`` aggregate in
  ``technology_trends`` with year-over-year growth and
  ``is_emerging`` / ``is_fast_growing`` flags.
* **Highly cited patents** — the top-N patents by citation count.
* **Similar patents** — cosine similarity (over the same TF-IDF
  matrix) to find patents similar to a given patent_id.

The implementation uses only scikit-learn (already a project
dependency) and numpy — there is no external ML service to deploy.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.patent import Patent, PatentCluster, TechnologyTrend


EMERGING_MIN_RECENT_YEARS = 2  # a technology needs 2+ recent years to be considered
EMERGING_RECENT_YEAR_WINDOW = 3  # look at the last N years for "recent"
EMERGING_GROWTH_THRESHOLD = 0.5  # YoY growth above 50% -> emerging
FAST_GROWING_THRESHOLD = 1.0  # YoY growth above 100% -> fast-growing


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _document_for(patent: Patent) -> str:
    """Concatenate the text fields used for TF-IDF."""
    parts = [
        patent.title or "",
        patent.abstract or "",
        patent.keywords or "",
        patent.technology_area or "",
    ]
    return " ".join(p for p in parts if p).strip()


def _safe_optimal_k(n_samples: int) -> int:
    """Heuristic for the K-Means k parameter.

    We want at least 2 clusters but no more than ``n_samples`` (and
    no more than 6 — the dashboard is for humans, not for an ML
    competition).  When the corpus is small we fall back to 2.
    """
    if n_samples < 2:
        return 2
    return max(2, min(6, n_samples))


def _top_terms(feature_names: np.ndarray, centroid: np.ndarray, k: int = 5) -> List[str]:
    """Return the top-k terms for a K-Means centroid."""
    top_idx = centroid.argsort()[::-1][:k]
    return [str(feature_names[i]) for i in top_idx if centroid[i] > 0]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class TechnologyIntelligenceService:
    """Stateless service for the technology intelligence layer."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def full_report(self) -> Dict[str, Any]:
        """Return the full technology intelligence report."""
        return {
            "emerging_technologies": self.emerging_technologies(),
            "fast_growing_technologies": self.fast_growing_technologies(),
            "highly_cited_patents": self.highly_cited_patents(),
            "clusters": self.cluster_patents(),
        }

    # ------------------------------------------------------------------
    # Clustering
    # ------------------------------------------------------------------
    def cluster_patents(self, *, force: bool = False) -> List[Dict[str, Any]]:
        """Run K-Means over the corpus and persist the result.

        Idempotent: re-running with ``force=False`` returns the
        current cached cluster rows without recomputing.
        """
        if not force:
            existing = self.db.query(PatentCluster).all()
            if existing:
                return [self._cluster_to_dict(c) for c in existing]

        patents = self.db.query(Patent).filter(Patent.title.isnot(None)).all()
        if not patents:
            return []

        docs = [_document_for(p) for p in patents]
        # Strip empty docs to keep the vectorizer happy.
        keep_idx = [i for i, d in enumerate(docs) if d]
        if len(keep_idx) < 2:
            return []

        patents = [patents[i] for i in keep_idx]
        docs = [docs[i] for i in keep_idx]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=2000,
            ngram_range=(1, 2),
            min_df=1,
        )
        try:
            matrix = vectorizer.fit_transform(docs)
        except ValueError:
            # Empty vocabulary — corpus is too small / repetitive.
            return []
        if matrix.shape[1] == 0:
            return []

        feature_names = np.array(vectorizer.get_feature_names_out())
        k = _safe_optimal_k(len(patents))
        try:
            km = KMeans(n_clusters=k, n_init=10, random_state=42)
            labels = km.fit_predict(matrix)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception(f"[tech-intel] KMeans failed: {exc}")
            return []

        # Build cluster aggregates and persist them.
        self._reset_clusters()
        cluster_rows: Dict[int, PatentCluster] = {}
        for patent, label in zip(patents, labels):
            label = int(label)
            if label not in cluster_rows:
                cluster_rows[label] = PatentCluster(
                    cluster_label=None,
                    size=0,
                    centroid_keywords=[],
                )
                self.db.add(cluster_rows[label])
            cluster_rows[label].size += 1  # type: ignore[operator]
            patent.cluster_id = None  # reset before re-assignment

        # Persist clusters first so we can set FKs.
        self.db.flush()

        # Compute labels from centroid top terms.
        for label, row in cluster_rows.items():
            top_terms = _top_terms(feature_names, km.cluster_centers_[label], k=5)
            row.cluster_label = " / ".join(top_terms[:3]) if top_terms else f"Cluster {label}"
            row.centroid_keywords = top_terms

        # Re-assign each patent's cluster_id and persist.
        for patent, label in zip(patents, labels):
            patent.cluster_id = cluster_rows[int(label)].id
        self.db.commit()

        return [self._cluster_to_dict(c) for c in cluster_rows.values()]

    def _reset_clusters(self) -> None:
        """Clear existing cluster assignments before a fresh run."""
        self.db.query(Patent).update({Patent.cluster_id: None})
        self.db.query(PatentCluster).delete()
        self.db.commit()

    @staticmethod
    def _cluster_to_dict(c: PatentCluster) -> Dict[str, Any]:
        return {
            "cluster_id": c.id,
            "label": c.cluster_label,
            "size": c.size,
            "keywords": c.centroid_keywords or [],
        }

    # ------------------------------------------------------------------
    # Trend detection
    # ------------------------------------------------------------------
    def recompute_trends(self) -> List[Dict[str, Any]]:
        """Refresh ``technology_trends`` from the current patent corpus."""
        rows = (
            self.db.query(
                Patent.technology_area,
                Patent.publication_year,
                func.count(Patent.id),
                func.coalesce(func.sum(Patent.citations), 0),
            )
            .filter(Patent.technology_area.isnot(None))
            .filter(Patent.publication_year.isnot(None))
            .group_by(Patent.technology_area, Patent.publication_year)
            .all()
        )
        # Sort by (technology_area, year) so we can compute YoY.
        rows = sorted(
            rows,
            key=lambda r: ((r[0] or ""), int(r[1] or 0)),
        )

        # Replace existing rows.
        self.db.query(TechnologyTrend).delete()
        self.db.flush()

        prev: Dict[str, int] = {}
        for tech, year, count, cites in rows:
            tech_str = tech or "Unclassified"
            year_int = int(year)
            prev_count = prev.get(tech_str)
            growth = None
            if prev_count:
                growth = round((count - prev_count) / prev_count, 4)
            row = TechnologyTrend(
                technology_area=tech_str,
                publication_year=year_int,
                patent_count=int(count),
                total_citations=int(cites or 0),
                growth_rate=growth,
                is_emerging=False,
                is_fast_growing=False,
            )
            self.db.add(row)
            prev[tech_str] = int(count)

        # Second pass: mark emerging / fast growing.
        all_rows = self.db.query(TechnologyTrend).all()
        max_year = max((r.publication_year for r in all_rows), default=0)
        for row in all_rows:
            row.is_fast_growing = bool(
                row.growth_rate is not None and row.growth_rate >= FAST_GROWING_THRESHOLD
            )
            row.is_emerging = bool(
                row.publication_year >= max_year - EMERGING_RECENT_YEAR_WINDOW + 1
                and row.patent_count > 0
                and (
                    row.growth_rate is not None
                    and row.growth_rate >= EMERGING_GROWTH_THRESHOLD
                )
            )
        self.db.commit()

        return [self._trend_to_dict(r) for r in all_rows]

    def emerging_technologies(self) -> List[Dict[str, Any]]:
        # Make sure trends are fresh.
        if not self.db.query(TechnologyTrend).first():
            self.recompute_trends()
        rows = (
            self.db.query(TechnologyTrend)
            .filter(TechnologyTrend.is_emerging.is_(True))
            .order_by(TechnologyTrend.publication_year.desc(), TechnologyTrend.patent_count.desc())
            .all()
        )
        return [self._trend_to_dict(r) for r in rows]

    def fast_growing_technologies(self) -> List[Dict[str, Any]]:
        if not self.db.query(TechnologyTrend).first():
            self.recompute_trends()
        rows = (
            self.db.query(TechnologyTrend)
            .filter(TechnologyTrend.is_fast_growing.is_(True))
            .order_by(TechnologyTrend.growth_rate.desc())
            .all()
        )
        return [self._trend_to_dict(r) for r in rows]

    @staticmethod
    def _trend_to_dict(r: TechnologyTrend) -> Dict[str, Any]:
        return {
            "technology_area": r.technology_area,
            "publication_year": r.publication_year,
            "patent_count": r.patent_count,
            "total_citations": r.total_citations,
            "growth_rate": r.growth_rate,
            "is_emerging": bool(r.is_emerging),
            "is_fast_growing": bool(r.is_fast_growing),
        }

    # ------------------------------------------------------------------
    # Highly cited
    # ------------------------------------------------------------------
    def highly_cited_patents(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(Patent)
            .order_by(Patent.citations.desc(), Patent.publication_date.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": p.id,
                "patent_number": p.patent_number,
                "title": p.title,
                "source": p.source,
                "publication_year": p.publication_year,
                "technology_area": p.technology_area,
                "citations": p.citations,
                "assignee": p.assignee,
            }
            for p in rows
        ]

    # ------------------------------------------------------------------
    # Similar patents
    # ------------------------------------------------------------------
    def similar_patents(self, patent_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        target = self.db.query(Patent).filter(Patent.id == patent_id).one_or_none()
        if target is None:
            return []
        patents = (
            self.db.query(Patent)
            .filter(Patent.id != patent_id)
            .filter(Patent.title.isnot(None))
            .all()
        )
        if not patents:
            return []
        target_doc = _document_for(target)
        docs = [target_doc] + [_document_for(p) for p in patents]
        vectorizer = TfidfVectorizer(stop_words="english", max_features=2000, ngram_range=(1, 2))
        try:
            matrix = vectorizer.fit_transform(docs)
        except ValueError:
            return []
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        order = sims.argsort()[::-1][:top_k]
        out: List[Dict[str, Any]] = []
        for idx in order:
            sim = float(sims[idx])
            if sim <= 0:
                continue
            cand = patents[idx]
            out.append(
                {
                    "patent_id": cand.id,
                    "patent_number": cand.patent_number,
                    "title": cand.title,
                    "similarity": round(sim, 4),
                    "reason": self._explain_similarity(target, cand, sim),
                }
            )
        return out

    @staticmethod
    def _explain_similarity(target: Patent, candidate: Patent, sim: float) -> str:
        reasons: List[str] = []
        if target.technology_area and target.technology_area == candidate.technology_area:
            reasons.append(f"same technology area ({target.technology_area})")
        if target.assignee and target.assignee == candidate.assignee:
            reasons.append(f"same assignee ({target.assignee})")
        if target.classification and target.classification == candidate.classification:
            reasons.append("same classification code")
        if not reasons:
            reasons.append("high TF-IDF cosine similarity on title+abstract+keywords")
        return "; ".join(reasons)
