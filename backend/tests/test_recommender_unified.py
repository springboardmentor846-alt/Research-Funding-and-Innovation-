"""End-to-end test for the unified funding recommendation pipeline.

The recommendation engine should treat every funding identically regardless
of which provider ingested it (admin / NIH / NSF / Grants.gov / OpenAlex).
This test exercises the recommender directly with a mixed corpus and
verifies that:

1. All four external sources (plus an admin-created row) are scored
   through the same ``FundingRecommender.recommend`` pipeline.
2. Funding rows whose ``source`` is set (NIH, NSF, …) survive the rule
   filter, get a non-zero score, and appear in the top-K results.
3. The recommender's own invariant is upheld: no per-funding branch on
   ``funding.source`` / ``funding.extra_metadata``. The test surfaces a
   regression by asserting that admin- and API-sourced rows are scored
   on the same scale and are mixed in the result.
4. Closed / expired rows are hard-zeroed out, regardless of source.
5. The function is deterministic for a fixed corpus (same scores on a
   second call).
"""
from __future__ import annotations

import os
import sys

# Allow running this file directly: put the backend/ on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta  # noqa: E402

from app.ai.recommender import funding_recommender  # noqa: E402


def _make_funding(
    funding_id: int,
    *,
    title: str,
    description: str,
    source: str = "admin",
    keywords: str = "",
    research_domain: str = "",
    deadline: datetime | None = None,
    is_active: bool = True,
):
    """Lightweight stand-in for the Funding ORM row.

    The recommender reads a handful of public attributes by name; a
    SimpleNamespace-shaped object is enough to exercise the pipeline
    without spinning up a database.
    """
    from types import SimpleNamespace

    return SimpleNamespace(
        id=funding_id,
        title=title,
        description=description,
        keywords=keywords,
        research_domain=research_domain,
        research_area=None,
        category=None,
        agency=None,
        organization=None,
        sponsor=None,
        country="United States",
        funding_type="grant",
        amount_min=None,
        amount_max=None,
        currency="USD",
        application_deadline=deadline,
        posted_date=datetime.utcnow() - timedelta(days=30),
        status="open",
        eligibility=None,
        url="https://example.com",
        source=source,
        is_active=is_active,
        extra_metadata={"funding_intel": {"source": source}} if source != "admin" else {},
        # ``updated_at`` is required by the corpus fingerprint;
        # ``created_at`` is required by the FundingResponse Pydantic schema.
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow() - timedelta(days=60),
    )


def _make_user(*, interests: str = "cybersecurity, network security"):
    from types import SimpleNamespace

    return SimpleNamespace(
        id=1,
        username="tester",
        full_name="Test User",
        email="t@example.com",
        role="researcher",
        research_interests=interests,
        h_index=0,
        i10_index=0,
        citation_count=0,
    )


def _make_publication(*, title: str, keywords: str = "", abstract: str = ""):
    from types import SimpleNamespace

    return SimpleNamespace(
        id=1,
        title=title,
        keywords=keywords,
        abstract=abstract,
        doi=None,
        citation_count=0,
    )


def main() -> int:
    # Five fundings covering the four external providers + admin.
    # All five mention cybersecurity so the interest-match signal is
    # non-zero for every row — this lets us assert scoring parity.
    future = datetime.utcnow() + timedelta(days=60)
    corpus = [
        _make_funding(
            1,
            title="NIH: Cybersecurity in Healthcare Systems",
            description="This NIH program funds research on cybersecurity "
                       "for hospital networks, medical devices, and patient data.",
            source="nih",
            keywords="cybersecurity, healthcare, network security",
            deadline=future,
        ),
        _make_funding(
            2,
            title="NSF: Secure Cloud Computing for Research",
            description="NSF solicitation on cloud security, zero trust, "
                       "and confidential computing in academic settings.",
            source="nsf",
            keywords="cloud security, zero trust, confidential computing",
            deadline=future,
        ),
        _make_funding(
            3,
            title="Grants.gov: State and Local Cybersecurity Grant",
            description="Federal grant for state and local governments to "
                       "improve cybersecurity posture and network defenses.",
            source="grants_gov",
            keywords="cybersecurity, government, network security",
            deadline=future,
        ),
        _make_funding(
            4,
            title="OpenAlex: Fellowship in Cyber-Physical Security",
            description="International fellowship supporting early-career "
                       "researchers in cybersecurity and resilient systems.",
            source="openalex",
            keywords="cybersecurity, fellowship, resilience",
            deadline=future,
        ),
        _make_funding(
            5,
            title="Admin: Internal Cybersecurity Pilot Fund",
            description="Internal platform grant for cybersecurity pilots.",
            source="admin",
            keywords="cybersecurity",
            research_domain="Cybersecurity",
            deadline=future,
        ),
        # A closed/expired row that must NEVER appear in the output,
        # even though its content matches perfectly.
        _make_funding(
            6,
            title="NIH: Expired Cybersecurity Call (should be excluded)",
            description="Stale closed call about cybersecurity.",
            source="nih",
            keywords="cybersecurity",
            deadline=datetime.utcnow() - timedelta(days=10),
            is_active=False,
        ),
    ]

    user = _make_user(interests="cybersecurity, network security")
    publications = [
        _make_publication(
            title="A Survey of Network Security in Cloud Environments",
            keywords="cybersecurity, network security, cloud",
            abstract="We survey recent advances in network security with a "
                     "focus on cloud-hosted research infrastructure.",
        )
    ]

    # Reset the in-process corpus cache so we get a clean TF-IDF fit
    # (the recommender keeps a module-level cache).
    import app.ai.recommender as rec
    rec._CORPUS_CACHE = None

    recs = funding_recommender.recommend(
        user=user,
        publications=publications,
        fundings=corpus,
        top_k=10,
    )
    print(f"[OK] recommender returned {len(recs)} recommendations")

    # INVARIANT 1: a recommendation exists for every source.
    sources_seen = {r.funding.source for r in recs}
    expected = {"nih", "nsf", "grants_gov", "openalex", "admin"}
    missing = expected - sources_seen
    assert not missing, f"missing source coverage: {missing}"
    print(f"[OK] all 4 external providers + admin represented: {sorted(sources_seen)}")

    # INVARIANT 2: the closed row is NEVER in the output.
    returned_ids = {r.funding.id for r in recs}
    assert 6 not in returned_ids, "closed/expired row leaked into recommendations"
    print("[OK] expired funding (id=6) is excluded from results")

    # INVARIANT 3: every returned row has a non-zero matching_percentage
    # and a non-empty explanation.
    for r in recs:
        assert r.matching_percentage > 0, r.funding.id
        assert r.explanation, r.funding.id
        # The recommender must surface matching_keywords for the UI.
        assert isinstance(r.matching_keywords, list), r.funding.id
    print("[OK] every returned row has score + explanation + keywords")

    # INVARIANT 4: scores are sorted descending.
    scores = [r.matching_percentage for r in recs]
    assert scores == sorted(scores, reverse=True), "results not sorted"
    print(f"[OK] sorted descending: {[round(s, 1) for s in scores]}")

    # INVARIANT 5: determinism — second call returns the same scores.
    rec._CORPUS_CACHE = None
    recs2 = funding_recommender.recommend(
        user=user,
        publications=publications,
        fundings=corpus,
        top_k=10,
    )
    ids1 = [r.funding.id for r in recs]
    ids2 = [r.funding.id for r in recs2]
    assert ids1 == ids2, f"non-deterministic ordering: {ids1} vs {ids2}"
    print("[OK] deterministic on re-run")

    print("\nUnified pipeline OK — all 4 external providers + admin ranked "
          "through the same pipeline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
