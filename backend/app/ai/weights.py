"""Default weights and thresholds for the AI recommender.

Only two signals drive the final score (per the product spec):

* ``publication_similarity`` — TF-IDF cosine over publication titles /
  keywords / abstracts vs funding text. Default weight ``0.60``.
* ``user_interests`` — semantic overlap between the user's expanded
  research interest set and the funding text. Default weight ``0.40``.

The remaining keys (``research_keywords``, ``eligibility``,
``history_penalty``) are kept here for backward-compat reads in the admin
UI and external dashboards, but they are no longer consumed by
``FundingRecommender.recommend``.

Thresholds:

* ``similarity_threshold`` — minimum cosine similarity that counts as a
  rule-5 pass in the rule-based pre-filter. Default ``0.08``.
* ``min_final_score`` — minimum combined score for a funding to be
  persisted to the cache / returned. Default ``0.05``.

Defaults are merged with anything stored under
``_PLATFORM_SETTINGS["ai_config"]["recommender_weights"]`` in admin.py,
so admins can tune via ``PUT /admin/settings`` without a restart.
"""
from __future__ import annotations

DEFAULT_AI_WEIGHTS: dict[str, float] = {
    # Two real signals
    "publication_similarity": 0.60,
    "user_interests": 0.40,
    # Thresholds
    "similarity_threshold": 0.08,
    "min_final_score": 0.05,
    # Legacy keys — kept for backward-compat reads; not used by the v2 engine.
    "research_keywords": 0.00,
    "eligibility": 0.00,
    "history_penalty": 0.00,
}


def merged_weights(overrides: dict | None = None) -> dict[str, float]:
    """Return DEFAULT_AI_WEIGHTS overridden by the supplied dict.

    Only known keys are accepted; unknown keys are ignored to keep the
    engine's contract tight.
    """
    if not overrides:
        return dict(DEFAULT_AI_WEIGHTS)
    merged = dict(DEFAULT_AI_WEIGHTS)
    for k, v in overrides.items():
        if k in merged and isinstance(v, (int, float)):
            merged[k] = float(v)
    return merged


def load_weights_from_settings() -> dict[str, float]:
    """Read weights from the admin in-memory settings if available.

    Imported lazily to avoid a circular import between the AI recommender and
    the admin module at app boot.
    """
    try:
        from app.api.v1.admin import _PLATFORM_SETTINGS  # late import
    except Exception:
        return dict(DEFAULT_AI_WEIGHTS)
    ai_cfg = _PLATFORM_SETTINGS.get("ai_config") or {}
    overrides = ai_cfg.get("recommender_weights") or {}
    return merged_weights(overrides)
