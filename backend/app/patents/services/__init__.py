"""Patent Intelligence services.

The services module collects the business logic for the Patent
Analytics & Innovation Intelligence platform.  Submodules are
intentionally small and focused so they can be tested independently:

* ``ingest`` — turns ``NormalizedPatent`` rows into ``Patent``
  SQLAlchemy rows, with cross-source dedup.
* ``sync`` — orchestrates provider runs and persists run metrics.
* ``landscape_service`` — patent landscape analysis.
* ``technology_intel_service`` — TF-IDF + KMeans, emerging tech,
  similarity.
* ``innovation_scoring_service`` — per-patent 5-factor score.
* ``commercialization_service`` — label rules + ranking.
* ``dashboard_service`` — orchestration + cache.
"""
