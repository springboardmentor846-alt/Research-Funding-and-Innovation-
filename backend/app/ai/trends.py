"""
Trend detection service.

Detects emerging research trends, citation growth, and domain analytics
from user publications and a synthesized dataset.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import List

from app.models.publication import Publication
from app.ai.text_preprocessing import TextPreprocessor


class TrendAnalyzer:
    """Detect research trends and domain analytics."""

    def __init__(self):
        self.preprocessor = TextPreprocessor()

    def extract_trending_keywords(self, publications: List[Publication], top_n: int = 20) -> list[dict]:
        """Return the most frequent keywords across the user's publications."""
        counter: Counter[str] = Counter()
        for p in publications:
            if p.keywords:
                for k in p.keywords.split(","):
                    k = k.strip().lower()
                    if k:
                        counter[k] += 1
            if p.title:
                counter.update(self.preprocessor.extract_keywords(p.title, top_n=10))
        return [{"keyword": k, "count": v} for k, v in counter.most_common(top_n)]

    def domain_distribution(self, publications: List[Publication]) -> list[dict]:
        """Distribution of publications by research domain."""
        dist: Counter[str] = Counter()
        for p in publications:
            dist[(p.research_domain or "Unspecified").strip()] += 1
        return [{"domain": d, "count": c} for d, c in dist.most_common()]

    def citation_trends(self, publications: List[Publication]) -> list[dict]:
        """Group citations by publication year."""
        buckets: dict[str, int] = defaultdict(int)
        for p in publications:
            year = str(p.publication_date.year) if p.publication_date else "Unknown"
            buckets[year] += p.citation_count or 0
        items = sorted(buckets.items(), key=lambda x: x[0])
        return [{"year": y, "citations": c} for y, c in items]

    def research_growth(self, publications: List[Publication]) -> list[dict]:
        """Count publications per year to visualize growth."""
        buckets: dict[str, int] = defaultdict(int)
        for p in publications:
            year = str(p.publication_date.year) if p.publication_date else "Unknown"
            buckets[year] += 1
        items = sorted(buckets.items(), key=lambda x: x[0])
        return [{"year": y, "publications": c} for y, c in items]

    def technology_evolution(self, publications: List[Publication]) -> list[dict]:
        """Top emerging technologies (proxy: most recent keywords)."""
        sorted_pubs = sorted(
            [p for p in publications if p.publication_date],
            key=lambda p: p.publication_date,
            reverse=True,
        )
        recent_keywords: Counter[str] = Counter()
        for p in sorted_pubs[: min(10, len(sorted_pubs))]:
            if p.keywords:
                for k in p.keywords.split(","):
                    k = k.strip().lower()
                    if k:
                        recent_keywords[k] += 1
        return [{"technology": k, "mentions": v} for k, v in recent_keywords.most_common(15)]


trend_analyzer = TrendAnalyzer()
