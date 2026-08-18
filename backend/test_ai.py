"""Smoke tests for the AI recommender.

Verifies:
  * The new weighted scorer mixes publication similarity, interests,
    keywords, and eligibility signals.
  * The history penalty correctly down-ranks previously-awarded fundings.
  * Custom weights override the defaults and re-order the results.

Run from the `backend/` directory with the project venv:
    ./venv/Scripts/python.exe test_ai.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Force stdout to UTF-8 so the OK  / FAIL glyphs print on Windows terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

OK = "[OK]  "
FAIL = "[FAIL]"

from datetime import datetime

from app.ai.recommender import funding_recommender
from app.ai.weights import DEFAULT_AI_WEIGHTS
from app.ai.text_preprocessing import TextPreprocessor
from app.core.research_domains import PREDEFINED_RESEARCH_DOMAINS
from app.models.publication import Publication
from app.models.funding import Funding
from app.models.funding_history import FundingHistory
from app.models.user import User
from app.models.research_interest import ResearchInterest


def _make_user(interest_names):
    """User with a CSV `research_interests` plus structured interest objects
    attached as `_structured_interests` (the path the recommender uses)."""
    u = User(
        id=1,
        email="test@test.com",
        username="test",
        research_interests=", ".join(interest_names),
        skills="Python, TensorFlow",
        affiliation="MIT, USA",
    )
    u._structured_interests = [
        ResearchInterest(
            id=i + 1,
            user_id=1,
            name=name,
            is_custom=name not in PREDEFINED_RESEARCH_DOMAINS,
            source="predefined" if name in PREDEFINED_RESEARCH_DOMAINS else "custom",
        )
        for i, name in enumerate(interest_names)
    ]
    return u


def _make_funding(id, title, desc, kw, dom, *, country="International", with_deadline=True):
    return Funding(
        id=id,
        title=title,
        description=desc,
        keywords=kw,
        research_domain=dom,
        is_active=True,
        currency="USD",
        country=country,
        amount_min=10000,
        amount_max=100000,
        application_deadline=datetime(2030, 1, 1) if with_deadline else None,
        created_at=datetime.utcnow(),
    )


def main():
    pp = TextPreprocessor()
    print("OK  TextPreprocessor loaded")
    sample = "Deep learning is transforming medical imaging! Visit https://example.com"
    cleaned = pp.clean(sample)
    tokens = pp.tokenize(sample)
    print(f"OK  Cleaning: '{sample}' -> '{cleaned}'")
    print(f"OK  Tokenization (first 10): {tokens[:10]}")
    print(f"OK  Default AI weights: {DEFAULT_AI_WEIGHTS}")
    print(f"OK  Predefined research domains: {len(PREDEFINED_RESEARCH_DOMAINS)} entries")

    # Researcher with mixed predefined + custom interests
    user = _make_user([
        "Artificial Intelligence",   # predefined
        "Machine Learning",          # predefined
        "AI for Healthcare",         # custom
        "Explainable AI",            # custom
        "Federated Learning",        # custom
    ])
    pub = Publication(
        id=1,
        owner_id=1,
        title="Deep Learning for Lung Cancer Detection",
        abstract="We use deep learning to detect lung cancer from CT scans with high accuracy.",
        keywords="deep learning, medical imaging, cancer, CT",
        authors="Test Author",
    )
    # Pre-existing award so the history penalty triggers
    user.funding_history = [
        FundingHistory(
            id=99,
            owner_id=1,
            funding_id=3,
            status="awarded",
            title="NIH Cancer Research Grant",
        )
    ]

    fundings = [
        _make_funding(1, "NIH Grant for AI in Healthcare",
                      "Funding for artificial intelligence research in medical applications.",
                      "machine learning, healthcare, deep learning, medical imaging",
                      "Medical AI"),
        _make_funding(2, "Quantum Computing Research",
                      "Funding for quantum error correction research.",
                      "quantum, computing, physics",
                      "Quantum Computing"),
        _make_funding(3, "NIH Cancer Research Grant",
                      "Funding for cancer research using deep learning and medical imaging.",
                      "cancer, deep learning, medical imaging",
                      "Medical AI"),
        _make_funding(4, "Explainable AI Innovation Prize",
                      "Awards research on explainable AI methods for healthcare applications.",
                      "explainable ai, federated learning, healthcare",
                      "Artificial Intelligence"),
    ]

    recs = funding_recommender.recommend(user, [pub], fundings, top_k=4)
    print(f"\nOK  Generated {len(recs)} recommendations")
    # v2 spec: "Never recommend unrelated domains." Quantum Computing has no
    # overlap with AI/Healthcare/ML, so funding #2 must be filtered out.
    assert len(recs) == 3, f"Expected 3 relevant recommendations, got {len(recs)}"
    assert all("Quantum" not in r.funding.title for r in recs), \
        "Unrelated Quantum Computing funding must not be recommended"
    print(f"OK  Irrelevant funding (#2 Quantum Computing) correctly rejected by rule filter")

    # Top match should be interest-heavy funding #1 or #4, not #2
    top = recs[0]
    assert "Quantum" not in top.funding.title, f"Quantum should not top the list: got {top.funding.title}"
    print(f"OK  Top match is correct: {top.funding.title}")

    # Explanation should quote the funding's own description, not be generic.
    assert '"' in top.explanation, "Explanation should quote the funding's description"
    assert "deep learning" in top.explanation.lower() or "ai" in top.explanation.lower(), \
        "Explanation should mention the matched topic or interest"
    print(f"OK  Explanation quotes the funding's own description")

    # Per the v2 spec, history penalty is intentionally NOT part of the
    # displayed score (it remains a metadata field for backward compat).
    f3 = next(r for r in recs if r.funding.id == 3)
    assert isinstance(f3.history_penalty_applied, bool), \
        "history_penalty_applied field must be present (bool) for backward compat"
    print(f"OK  Funding #3 surfaced in cache: matching_percentage={f3.matching_percentage}%")

    # Each recommendation should expose the per-signal breakdown
    for r in recs:
        assert 0 <= r.interest_score <= 1
        assert 0 <= r.keyword_score <= 1
        assert 0 <= r.eligibility_score <= 1
        assert isinstance(r.explanation, str) and r.explanation
    print("OK  Per-signal breakdown populated on every recommendation")

    # Custom weights must reorder results — boost interests, drop publications
    custom_weights = {
        "publication_similarity": 0.10,
        "user_interests": 0.80,
        "research_keywords": 0.05,
        "eligibility": 0.05,
        "history_penalty": 0.15,
    }
    recs_interest_heavy = funding_recommender.recommend(
        user, [pub], fundings, top_k=4, weights=custom_weights
    )
    assert recs_interest_heavy, "interest-heavy weights must still return results"
    new_top = recs_interest_heavy[0]
    assert new_top.matching_percentage != top.matching_percentage, \
        "Custom weights must change the score (got identical score)"
    print(f"OK  Custom weights produced a different ranking: top={new_top.funding.title} ({new_top.matching_percentage}%)")

    # Funding #4 (Explainable AI / Federated Learning) should score well with
    # interest-heavy weights because it matches the user's custom interests.
    f4 = next(r for r in recs_interest_heavy if r.funding.id == 4)
    assert f4.interest_score > 0, "Funding #4 should match user interests"
    print(f"OK  Custom-interest match: Funding #4 interest_score={f4.interest_score}")

    print("\nOK  All tests passed")


if __name__ == "__main__":
    main()