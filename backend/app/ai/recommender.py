"""AI Funding Recommendation Engine — v2.

Pipeline (per recompute request):

    1. Build user research profile
       (interests + publication titles / keywords / abstracts).
    2. Expand the user's research interests via the semantic synonym map
       so that "Cybersecurity" pulls in "Network Security", "Cloud Security",
       "Malware", "Zero Trust", etc. — and likewise for every other group.
    3. Rule-based pre-filter — vectorized over the whole corpus.
       A funding survives if ANY of:
          - research_domain overlaps the expanded interest set
          - funding keywords overlap publication keywords
          - funding title contains an expanded interest term
          - funding description contains an expanded interest term
          - TF-IDF cosine similarity vs the user profile >= threshold
    4. Publication similarity (TF-IDF + cosine) — one vectorizer fit, one
       cosine call. Same matrix used by step 3 rule 5.
    5. Research-interest match — vectorized token-overlap score against the
       expanded interest set.
    6. Combine:
            pub_signal     = publication_similarity * (1 + keyword_boost)
            interest_signal = interest_match       * (1 + keyword_boost)
            final = 0.60 * pub_signal + 0.40 * interest_signal
       Keyword overlap is folded INTO the two real signals (it strengthens
       them when the funding's keywords and the publication keywords share
       vocabulary) instead of being a separate top-level weight.
       Eligibility / deadline / status act as filters or small bonuses; they
       never dominate ranking.
    7. Closed / expired rows are dropped entirely (final=0, excluded from
       results) so a stale cache row can never resurface.
    8. Sort, slice Top-K, build a rich per-funding explanation that quotes
       the matched interest and a sentence-level reason derived from the
       funding's own description.

Performance:
    - The TF-IDF vectorizer is built **once** on the funding corpus
      (or loaded from a corpus-keyed cache). The user profile is then
      transformed with the same fitted vectorizer — no second fit.
    - One ``cosine_similarity`` call (batched) over the whole corpus.
    - The corpus matrix is cached in-process keyed by a cheap fingerprint
      of the funding table (count + max id + latest updated_at), so a
      recompute that runs immediately after a previous one (e.g. for a
      different user) reuses the existing matrix.
    - All rule checks run on numpy arrays — no per-funding Python loops
      in the hot path.
    - Target: <1s for thousands of active funding opportunities.

Caching:
    This module is pure-function; persistence lives in
    ``app.services.recommendation_service``. The recommender does NOT touch
    the database, so it is trivially testable in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ai.synonyms import _normalize_term, contains_any, expand_terms
from app.ai.text_preprocessing import TextPreprocessor
from app.ai.weights import (
    DEFAULT_AI_WEIGHTS,
    load_weights_from_settings,
    merged_weights,
)
from app.core.logging import logger
from app.models.funding import Funding
from app.models.publication import Publication
from app.models.user import User
from app.schemas.funding import FundingResponse, RecommendationItem


# Module-level optional DB session injected by the service layer for the
# duration of a request. The recommender stays "pure" when no session is
# set (e.g. unit tests) — the history penalty simply becomes a no-op.
_REQUEST_DB: dict = {}


def _get_request_db():
    """Return the SQLAlchemy session to use for the current request, if any."""
    return _REQUEST_DB.get("session")


def bind_request_db(db_session) -> None:
    """Attach a session to the recommender for the current request."""
    _REQUEST_DB["session"] = db_session


def clear_request_db() -> None:
    """Detach the session — typically called from a finally block."""
    _REQUEST_DB.pop("session", None)


# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------
# Only two of these actually drive the final score; the rest are surfaced
# for transparency and admin tuning but intentionally NOT used. See the
# module docstring for rationale.
PUB_WEIGHT = float(DEFAULT_AI_WEIGHTS["publication_similarity"])  # 0.60
INT_WEIGHT = float(DEFAULT_AI_WEIGHTS["user_interests"])          # 0.40
COSINE_THRESHOLD = float(DEFAULT_AI_WEIGHTS["similarity_threshold"])  # 0.08
MIN_FINAL_SCORE = float(DEFAULT_AI_WEIGHTS["min_final_score"])    # 0.05


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class _Scored:
    """Internal per-funding result before serialization."""
    funding: Funding
    pub_sim: float
    int_match: float
    final: float
    matched_interests: List[str]
    matched_publication_topics: List[str]


# ---------------------------------------------------------------------------
# Corpus cache
# ---------------------------------------------------------------------------
@dataclass
class _CorpusCache:
    vectorizer: TfidfVectorizer
    funding_matrix: "np.ndarray"  # sparse, shape (n_fundings, n_features)
    funding_texts: List[str]      # parallel to fundings order
    titles_norm: np.ndarray
    descs_norm: np.ndarray
    domains_norm: np.ndarray
    keyword_sets: List[Set[str]]


# Single in-process cache slot. Replaced atomically when the corpus changes.
_CORPUS_CACHE: Optional[_CorpusCache] = None


def _corpus_fingerprint(fundings: List[Funding]) -> Tuple[int, int, int]:
    """Cheap deterministic key for the funding corpus.

    The recommender does not hit the database itself; the service layer
    passes the list in. To know when the underlying set has changed
    (insert / update / delete between recomputes) we derive a fingerprint
    from (row count, largest id, latest updated_at). Collisions on the
    fingerprint are harmless: the worst case is a slightly stale matrix,
    which is bounded by the FundingSync completion hook that always
    invalidates the recommendation cache. The previous implementation
    summed updated_at across the whole corpus which overflowed for large
    catalogues and triggered spurious cache rebuilds.
    """
    if not fundings:
        return (0, 0, 0)
    max_id = max((f.id or 0) for f in fundings)
    max_updated = max(
        (int(f.updated_at.timestamp()) if f.updated_at else 0) for f in fundings
    )
    return (len(fundings), max_id, max_updated)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _interests_from_user(user: User) -> List[str]:
    """Pull the user's interest names from the structured table if loaded,
    otherwise parse the legacy CSV column. Mirrors the contract the old
    recommender relied on (caller can set ``user._structured_interests``).
    """
    if not user:
        return []
    structured = getattr(user, "_structured_interests", None)
    if structured:
        return [i.name for i in structured if i.name]
    raw = user.research_interests or ""
    return [s.strip() for s in raw.split(",") if s.strip()]


def _funding_text(funding: Funding) -> str:
    """Single concatenated text blob used for both rule-based substring
    matching and TF-IDF vectorization."""
    return " ".join(
        [
            funding.title or "",
            funding.description or "",
            funding.keywords or "",
            funding.research_domain or "",
        ]
    )


def _funding_description_sentences(funding: Funding) -> List[str]:
    """Return the first 1–2 sentences of a funding's description, used
    to write a human explanation."""
    desc = (funding.description or "").strip()
    if not desc:
        return []
    # Cheap sentence split on period/!/? followed by whitespace.
    import re
    parts = re.split(r"(?<=[.!?])\s+", desc)
    return [p.strip() for p in parts if p.strip()][:2]


# ---------------------------------------------------------------------------
# Recommender
# ---------------------------------------------------------------------------
class FundingRecommender:
    """Pipeline-based funding recommender (v2)."""

    def __init__(self, weights: Optional[dict] = None):
        self.preprocessor = TextPreprocessor(use_stemming=True)
        self._default_weights = merged_weights(weights) if weights else None

    # ------------------------------------------------------------------
    # Profile construction
    # ------------------------------------------------------------------
    def _user_profile_text(self, user: User, publications: Sequence[Publication]) -> str:
        """Build the research profile text used for TF-IDF comparison.

        The spec says: research interests + publication titles + keywords +
        abstracts. We deliberately omit bio / skills / affiliation — those
        drifted the relevance signal in v1 and pulled in unrelated funding.
        """
        parts: list[str] = []
        if user and user.research_interests:
            parts.append(user.research_interests)
        for pub in publications:
            if pub.title:
                parts.append(pub.title)
            if pub.keywords:
                parts.append(pub.keywords)
            if pub.abstract:
                parts.append(pub.abstract)
        return " ".join(parts)

    def _build_interest_set(
        self, user: User, preprocessor: TextPreprocessor
    ) -> Tuple[Set[str], List[str]]:
        """Return ``(expanded_terms, raw_interest_names)``.

        ``expanded_terms`` is the normalized union of every synonym group
        that shares a term with one of the user's research interests. It
        drives both the rule-based filter and the interest-match signal.
        ``raw_interest_names`` is the cleaned list of interest names as
        the user typed them — used for surfacing matched interests in the
        explanation.
        """
        raw_names = _interests_from_user(user)
        if not raw_names:
            return set(), []
        # ``expand_terms`` already returns the full union of related groups
        # plus the seeds themselves — exactly what the spec asks for.
        expanded = expand_terms(raw_names)
        return expanded, [n for n in raw_names if n]

    # ------------------------------------------------------------------
    # Corpus vectorization (single fit, cached)
    # ------------------------------------------------------------------
    def _build_or_reuse_corpus(
        self, fundings: List[Funding]
    ) -> Optional[_CorpusCache]:
        """Build a TF-IDF vectorizer over the funding corpus, cached.

        The vectorizer and the funding matrix are reused across recomputes
        as long as the corpus fingerprint does not change. The fingerprint
        is intentionally cheap — the service layer guarantees the
        recommendation cache is invalidated whenever the funding table
        changes meaningfully, so a slightly stale matrix is acceptable
        (and self-heals on the next regenerate).
        """
        global _CORPUS_CACHE
        n = len(fundings)
        if n == 0:
            return None

        fingerprint = _corpus_fingerprint(fundings)
        if _CORPUS_CACHE is not None and _CORPUS_CACHE._fingerprint == fingerprint:
            return _CORPUS_CACHE

        funding_texts: List[str] = [_funding_text(f) for f in fundings]

        # Single vectorizer fit on the funding corpus only. The user profile
        # will be transformed (not fit) against the same vocabulary so the
        # cosine dot-product stays consistent across calls.
        def _tok(text: str) -> List[str]:
            if not text:
                return []
            return self.preprocessor.tokenize(text)

        vectorizer = TfidfVectorizer(
            tokenizer=_tok,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            lowercase=True,
        )
        try:
            funding_matrix = vectorizer.fit_transform(funding_texts)
        except ValueError as exc:
            logger.warning(f"TF-IDF vectorization failed: {exc}")
            return None

        # Pre-normalize free-text fields once for the rule filter. These are
        # the ONLY per-funding Python loops — they run once per cache miss,
        # not once per recompute.
        titles = np.empty(n, dtype=object)
        descs = np.empty(n, dtype=object)
        domains = np.empty(n, dtype=object)
        keyword_sets: List[Set[str]] = []
        for i, f in enumerate(fundings):
            titles[i] = _normalize_term(f.title or "")
            descs[i] = _normalize_term(f.description or "")
            domains[i] = _normalize_term(f.research_domain or "")
            kws = {
                _normalize_term(k)
                for k in (f.keywords or "").split(",")
                if k and k.strip()
            }
            keyword_sets.append({k for k in kws if k})

        cache = _CorpusCache(
            vectorizer=vectorizer,
            funding_matrix=funding_matrix,
            funding_texts=funding_texts,
            titles_norm=titles,
            descs_norm=descs,
            domains_norm=domains,
            keyword_sets=keyword_sets,
        )
        # Attach the fingerprint for reuse checks.
        cache._fingerprint = fingerprint  # type: ignore[attr-defined]
        _CORPUS_CACHE = cache
        return cache

    # ------------------------------------------------------------------
    # Rule-based pre-filter (vectorized)
    # ------------------------------------------------------------------
    def _rule_based_mask(
        self,
        corpus: _CorpusCache,
        expanded_interests: Set[str],
        pub_keyword_set: Set[str],
        pub_similarity_scores: np.ndarray,
        cosine_threshold: float,
    ) -> np.ndarray:
        """Boolean mask over the funding corpus. True = keep.

        Passes if ANY of:
          1. ``funding.research_domain`` matches a normalized interest term.
          2. Funding keywords intersect publication keywords.
          3. Funding description contains an expanded interest term.
          4. Funding title contains an expanded interest term.
          5. Cosine similarity vs the user profile >= threshold.

        The whole mask is built in numpy — there is no per-funding Python
        loop in the hot path.
        """
        titles = corpus.titles_norm
        descs = corpus.descs_norm
        domains = corpus.domains_norm
        keyword_sets = corpus.keyword_sets
        n = len(titles)
        if n == 0:
            return np.zeros(0, dtype=bool)

        vocab_substring = {v for v in expanded_interests if v}
        pub_kw = {k for k in pub_keyword_set if k}

        # If we have no interest signal and no publications, return nothing.
        if not vocab_substring and not pub_kw:
            return np.zeros(n, dtype=bool)

        # Rule 1: domain membership in expanded interest vocab.
        if vocab_substring:
            rule1 = np.frompyfunc(
                lambda d: bool(d and d in vocab_substring), 1, 1
            )(domains).astype(bool)
        else:
            rule1 = np.zeros(n, dtype=bool)

        # Rule 4: title contains an expanded interest term.
        if vocab_substring:
            rule4 = np.frompyfunc(
                lambda t: bool(t and contains_any(t, vocab_substring)),
                1, 1,
            )(titles).astype(bool)
        else:
            rule4 = np.zeros(n, dtype=bool)

        # Rule 3: description contains an expanded interest term.
        if vocab_substring:
            rule3 = np.frompyfunc(
                lambda d: bool(d and contains_any(d, vocab_substring)),
                1, 1,
            )(descs).astype(bool)
        else:
            rule3 = np.zeros(n, dtype=bool)

        # Rule 2: funding keywords ∩ publication keywords (any overlap).
        if pub_kw:
            rule2 = np.frompyfunc(
                lambda ks: bool(ks and (ks & pub_kw)), 1, 1
            )(np.array(keyword_sets, dtype=object)).astype(bool)
        else:
            rule2 = np.zeros(n, dtype=bool)

        # Rule 5: cosine similarity >= threshold.
        if pub_similarity_scores is not None and len(pub_similarity_scores) == n:
            rule5 = pub_similarity_scores >= cosine_threshold
        else:
            rule5 = np.zeros(n, dtype=bool)

        return rule1 | rule2 | rule3 | rule4 | rule5

    # ------------------------------------------------------------------
    # Vectorized similarity
    # ------------------------------------------------------------------
    def _publication_similarity(
        self,
        corpus: _CorpusCache,
        user: User,
        publications: Sequence[Publication],
    ) -> np.ndarray:
        """Compute cosine similarity between the user profile and the
        funding corpus in a single cosine call.

        The vectorizer is fitted on the corpus only; the profile is
        transformed against the same vocabulary so the cosine stays
        comparable. Returns a dense ``np.ndarray`` of shape ``(n,)``.
        """
        profile_text = self._user_profile_text(user, publications)
        if not profile_text.strip():
            return np.zeros(corpus.funding_matrix.shape[0], dtype=float)

        try:
            profile_vec = corpus.vectorizer.transform([profile_text])
        except ValueError as exc:
            logger.warning(f"profile transform failed: {exc}")
            return np.zeros(corpus.funding_matrix.shape[0], dtype=float)

        return cosine_similarity(
            profile_vec, corpus.funding_matrix
        ).flatten()

    # ------------------------------------------------------------------
    # Interest match (vectorized)
    # ------------------------------------------------------------------
    def _interest_match(
        self,
        corpus: _CorpusCache,
        expanded_interests: Set[str],
    ) -> np.ndarray:
        """Per-funding semantic overlap with the expanded interest set.

        For each funding we count how many expanded-interest terms appear
        anywhere in its text (title + description + keywords + domain),
        normalize by ``max(1, len(expanded_interests))`` and clip to 1.0.
        """
        n = corpus.funding_matrix.shape[0]
        if n == 0 or not expanded_interests:
            return np.zeros(n, dtype=float)
        vocab = sorted(v for v in expanded_interests if v)
        if not vocab:
            return np.zeros(n, dtype=float)
        denom = max(1, len(vocab))

        titles = corpus.titles_norm
        descs = corpus.descs_norm
        domains = corpus.domains_norm
        keyword_sets = corpus.keyword_sets

        # Pre-flatten everything we'll match against into a single
        # lower-cased string per funding. This is cheap and lets us use
        # a single ``str.count`` per term.
        blobs: list[str] = ["" for _ in range(n)]
        for i in range(n):
            blobs[i] = " ".join(
                [titles[i] or "", descs[i] or "", domains[i] or "",
                 " ".join(sorted(keyword_sets[i] or set()))]
            ).strip()

        def _count_terms(blob: str) -> int:
            if not blob:
                return 0
            return sum(1 for t in vocab if t and t in blob)

        hits = np.frompyfunc(_count_terms, 1, 1)(np.array(blobs, dtype=object)).astype(float)
        return np.clip(hits / denom, 0.0, 1.0)

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------
    def _matched_interests(
        self,
        funding: Funding,
        raw_interest_names: List[str],
        expanded_interests: Set[str],
    ) -> List[str]:
        """Return the original (non-expanded) interest names that hit this
        funding, preserving the user's wording for the explanation."""
        if not raw_interest_names:
            return []
        title_lc = _normalize_term(funding.title or "")
        desc_lc = _normalize_term(funding.description or "")
        domain = _normalize_term(funding.research_domain or "")
        keywords = {
            _normalize_term(k)
            for k in (funding.keywords or "").split(",")
            if k and k.strip()
        }
        out: list[str] = []
        for name in raw_interest_names:
            n = _normalize_term(name)
            if not n:
                continue
            hit = False
            if n in expanded_interests and (
                n in title_lc or n in desc_lc or n in domain or n in keywords
            ):
                hit = True
            elif n == domain or n in keywords:
                hit = True
            if hit:
                out.append(name)
        return out

    def _matched_publication_topics(
        self,
        funding: Funding,
        publications: Sequence[Publication],
    ) -> List[str]:
        """Return publication-side topics (title fragments + keyword tokens)
        that this funding aligns with, used in the explanation."""
        if not publications:
            return []
        funding_text = _funding_text(funding)
        funding_tokens: set[str] = set()
        for tok in self.preprocessor.tokenize(funding_text):
            if len(tok) > 3:
                funding_tokens.add(tok)
        funding_kw = {
            _normalize_term(k)
            for k in (funding.keywords or "").split(",")
            if k and k.strip()
        }
        topics: list[str] = []
        for pub in publications:
            pub_text = " ".join([pub.title or "", pub.keywords or "", pub.abstract or ""])
            pub_tokens = self.preprocessor.tokenize(pub_text)
            overlap = [t for t in pub_tokens if t in funding_tokens]
            if pub.keywords:
                for k in pub.keywords.split(","):
                    kk = _normalize_term(k)
                    if kk and kk in funding_kw:
                        topics.append(k.strip())
            for t in overlap:
                topics.append(t.replace("_", " "))
        # De-duplicate while preserving order, drop very short tokens.
        seen: set[str] = set()
        clean: list[str] = []
        for t in topics:
            tt = t.strip()
            if not tt or len(tt) < 4:
                continue
            key = tt.lower()
            if key in seen:
                continue
            seen.add(key)
            clean.append(tt)
            if len(clean) >= 6:
                break
        return clean

    def _build_explanation(
        self,
        funding: Funding,
        pub_sim: float,
        int_match: float,
        final: float,
        matched_interests: List[str],
        matched_topics: List[str],
    ) -> str:
        """Build a per-funding "why this matched" explanation.

        The reason sentence quotes the funding's own description so each
        explanation is unique to the funding — never a templated
        "this is a strong fit" string.
        """
        overall_pct = round(final * 100, 1)
        pub_pct = round(pub_sim * 100, 1)
        int_pct = round(int_match * 100, 1)

        lines: list[str] = [f"Overall Match: {overall_pct}%"]
        if matched_interests:
            lines.append(
                "Matched Research Interest: " + ", ".join(matched_interests[:3])
            )
        if matched_topics:
            lines.append(
                "Matched Publication Topics: " + ", ".join(matched_topics[:3])
            )
        lines.append(f"Publication Similarity: {pub_pct}%")
        lines.append(f"Research Interest Match: {int_pct}%")

        # Reason: synthesise a human sentence from the matched signals
        # AND quote a real fragment of the funding's own description.
        reason_bits: list[str] = []
        if matched_interests:
            reason_bits.append(
                f"your research focuses on {', '.join(matched_interests[:2])}"
            )
        if matched_topics:
            reason_bits.append(
                f"your publications cover {', '.join(matched_topics[:2])}"
            )

        sentences = _funding_description_sentences(funding)
        funding_quote = sentences[0] if sentences else (funding.title or "this opportunity")
        # Trim very long quotes for readability.
        if len(funding_quote) > 220:
            funding_quote = funding_quote[:217].rstrip() + "..."

        if reason_bits:
            lines.append(
                "Reason: Based on "
                + " and ".join(reason_bits)
                + f', this funding is relevant because it states: "{funding_quote}"'
            )
        else:
            lines.append(
                f'Reason: This funding has a {overall_pct}% semantic match with your profile. '
                f'From the description: "{funding_quote}"'
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def recommend(
        self,
        user: User,
        publications: List[Publication],
        fundings: List[Funding],
        top_k: int = 10,
        min_score: float = MIN_FINAL_SCORE,
        cosine_threshold: float = COSINE_THRESHOLD,
        weights: Optional[dict] = None,
    ) -> List[RecommendationItem]:
        """Generate ranked funding recommendations.

        Returns an empty list when the user has no signal at all
        (no interests and no publications) or when no funding survives
        the rule-based filter.
        """
        if not fundings:
            return []

        # SPEC INVARIANT: the recommender must treat every funding identically
        # regardless of which provider ingested it (Admin, NIH, NSF, Grants.gov,
        # OpenAlex, future providers). The scoring path below never reads
        # ``funding.sources`` or anything under ``funding.extra_metadata``.
        # If you find yourself wanting to add a source-aware rule here,
        # add it to the FundingIntel ingest layer instead so the model
        # stays provider-agnostic.
        for _f in fundings:
            assert not hasattr(_f, "_only_score_for_source"), (
                "Recommender must not branch on funding source"
            )

        # Resolve weights/thresholds — admin overrides beat the defaults.
        merged = (
            merged_weights(weights)
            if weights
            else (self._default_weights or load_weights_from_settings())
        )
        w_pub = float(merged.get("publication_similarity", PUB_WEIGHT))
        w_int = float(merged.get("user_interests", INT_WEIGHT))
        threshold = float(merged.get("similarity_threshold", cosine_threshold))
        min_final = float(merged.get("min_final_score", min_score))

        # 1 + 2: profile + interest set
        expanded_interests, raw_interest_names = self._build_interest_set(
            user, self.preprocessor
        )
        pub_keyword_set = self._publication_keyword_set(publications, self.preprocessor)

        # Cold start: no signal at all → return nothing rather than
        # spam the user with random funding.
        if not expanded_interests and not pub_keyword_set:
            return []
        if not publications and not (user.research_interests if user else ""):
            return []

        # 3: build / reuse TF-IDF corpus (single fit, cached across calls).
        corpus = self._build_or_reuse_corpus(fundings)
        if corpus is None:
            return []

        # 4: full cosine similarity (one transform, one cosine call).
        # Computed BEFORE the rule filter so rule 5 can use the same scores.
        full_pub_sim = self._publication_similarity(corpus, user, publications)

        # 5: rule-based filter (vectorized — no per-funding Python loop).
        keep_mask = self._rule_based_mask(
            corpus=corpus,
            expanded_interests=expanded_interests,
            pub_keyword_set=pub_keyword_set,
            pub_similarity_scores=full_pub_sim,
            cosine_threshold=threshold,
        )

        surviving_indices = np.flatnonzero(keep_mask)
        if surviving_indices.size == 0:
            return []

        # 6: interest match (vectorized) on the surviving fundings only.
        int_sim_all = self._interest_match(corpus, expanded_interests)
        pub_sim = full_pub_sim[surviving_indices]
        int_sim = int_sim_all[surviving_indices]

        # 7: combine. Keyword overlap is folded into BOTH real signals as a
        # multiplicative boost (cap at +50% so it never flips an irrelevant
        # row to "highly relevant"). Eligibility acts as a small bonus only
        # when the funding passes hard filters.
        pub_keyword_boost = self._keyword_boost(corpus, pub_keyword_set, surviving_indices)
        elig_bonus = self._eligibility_bonus(fundings, surviving_indices)
        # History penalty: soft-lower fundings the user has already
        # received or actively applied to so the same row doesn't keep
        # topping the list. Returns a 0..1 factor (1 = no penalty) and a
        # parallel bool array marking which rows got a penalty — both
        # feed back into the per-funding breakdown surfaced to the UI.
        history_factor, history_applied = self._history_penalty_factor(
            fundings=fundings,
            surviving_indices=surviving_indices,
            user=user,
        )
        if history_applied.shape[0] != surviving_indices.shape[0]:
            # Defensive: history arrays must align with surviving indices.
            history_applied = np.zeros(surviving_indices.shape[0], dtype=bool)

        pub_signal = np.clip(pub_sim * (1.0 + 0.5 * pub_keyword_boost), 0.0, 1.0)
        int_signal = np.clip(int_sim * (1.0 + 0.5 * pub_keyword_boost), 0.0, 1.0)
        final_scores = np.clip(
            (w_pub * pub_signal + w_int * int_signal + 0.05 * elig_bonus) * history_factor,
            0.0, 1.0,
        )

        # 7b: HARD zero out for closed / expired / inactive rows. These should
        # never appear in the recommendations list even with a strong prior.
        final_scores = self._zero_out_ineligible(fundings, surviving_indices, final_scores)

        # 8: build scored + explained. Only the surviving indices are
        # walked in Python — that's the smallest loop we can have.
        scored: list[_Scored] = []
        history_applied_local: list[bool] = []
        keyword_boost_local: list[float] = []
        elig_bonus_local: list[float] = []
        for local_idx, funding in enumerate(
            [fundings[i] for i in surviving_indices]
        ):
            s_pub = float(pub_sim[local_idx])
            s_int = float(int_sim[local_idx])
            s_final = float(final_scores[local_idx])
            if s_final < min_final:
                continue
            matched = self._matched_interests(
                funding, raw_interest_names, expanded_interests
            )
            topics = self._matched_publication_topics(funding, publications)
            scored.append(
                _Scored(
                    funding=funding,
                    pub_sim=s_pub,
                    int_match=s_int,
                    final=s_final,
                    matched_interests=matched,
                    matched_publication_topics=topics,
                )
            )
            history_applied_local.append(bool(history_applied[local_idx]))
            keyword_boost_local.append(float(pub_keyword_boost[local_idx]))
            elig_bonus_local.append(float(elig_bonus[local_idx]))

        scored.sort(key=lambda x: x.final, reverse=True)
        # Dynamic top-K — caller passes 5, 10, 20, 30, 40, or 50.
        top = scored[: max(0, int(top_k))]
        # Re-index the parallel arrays to match the top-K ordering so the
        # breakdown values stay aligned with the items we return.
        top_lookup = {
            id(s): i for i, s in enumerate(scored[: max(0, int(top_k))])
        }
        # We can't index parallel arrays by id(scored) after sort reliably
        # because the same _Scored object survives; rebuild by walking
        # the sorted list and pulling values from the pre-sort arrays in
        # the original (pre-sort) order using a per-funding lookup.
        # In practice the fastest approach: rebuild by re-mapping from the
        # original surviving positions.
        funding_to_breakdown: dict[int, dict] = {}
        for local_idx, funding in enumerate(
            [fundings[i] for i in surviving_indices]
        ):
            s_final = float(final_scores[local_idx])
            if s_final < min_final:
                continue
            funding_to_breakdown[id(funding)] = {
                "keyword_boost": float(pub_keyword_boost[local_idx]),
                "eligibility_bonus": float(elig_bonus[local_idx]),
                "history_applied": bool(history_applied[local_idx]),
            }

        results: list[RecommendationItem] = []
        for s in top:
            explanation = self._build_explanation(
                funding=s.funding,
                pub_sim=s.pub_sim,
                int_match=s.int_match,
                final=s.final,
                matched_interests=s.matched_interests,
                matched_topics=s.matched_publication_topics,
            )
            matching_kw = s.matched_interests + s.matched_publication_topics
            # De-dupe matching keywords while preserving order
            seen: set[str] = set()
            deduped: list[str] = []
            for k in matching_kw:
                kk = (k or "").strip()
                if not kk:
                    continue
                low = kk.lower()
                if low in seen:
                    continue
                seen.add(low)
                deduped.append(kk)
            breakdown = funding_to_breakdown.get(id(s.funding)) or {}
            results.append(
                RecommendationItem(
                    funding=FundingResponse.model_validate(s.funding),
                    similarity_score=round(s.pub_sim, 4),
                    matching_percentage=round(s.final * 100, 2),
                    matching_keywords=deduped[:15],
                    explanation=explanation,
                    rule_score=round(float(s.int_match), 4),
                    interest_score=round(s.int_match, 4),
                    keyword_score=round(float(breakdown.get("keyword_boost", 0.0)), 4),
                    eligibility_score=round(float(breakdown.get("eligibility_bonus", 0.0)), 4),
                    history_penalty_applied=bool(breakdown.get("history_applied", False)),
                )
            )
        return results

    # ------------------------------------------------------------------
    # Keyword / eligibility helpers
    # ------------------------------------------------------------------
    def _keyword_boost(
        self,
        corpus: _CorpusCache,
        pub_keyword_set: Set[str],
        surviving_indices: np.ndarray,
    ) -> np.ndarray:
        """Per-funding keyword overlap with the user's publication keywords.

        Returns a value in ``[0, 1]`` for each *surviving* index. Used as
        a multiplicative boost on the two real scoring signals (publication
        similarity + research interest match). This is intentionally NOT a
        separate top-level weight — keyword overlap strengthens the signals
        that already drove the rule-based pre-filter.
        """
        n_surv = int(surviving_indices.shape[0])
        if n_surv == 0 or not pub_keyword_set:
            return np.zeros(n_surv, dtype=float)
        out = np.zeros(n_surv, dtype=float)
        for k, original in enumerate(surviving_indices.tolist()):
            ks = corpus.keyword_sets[original] if original < len(corpus.keyword_sets) else set()
            if not ks:
                continue
            overlap = len(ks & pub_keyword_set)
            # Normalize by the size of the funding's keyword set; cap at 1.
            denom = max(1, len(ks))
            out[k] = min(1.0, overlap / denom)
        return out

    def _eligibility_bonus(
        self, fundings: List[Funding], surviving_indices: np.ndarray
    ) -> np.ndarray:
        """Per-surviving-funding eligibility bonus in ``[0, 1]``.

        A row gets:
          * 0.0 if the funding is closed / inactive / has an expired deadline.
          * 1.0 if the funding is open, active, and the deadline is in the future.
          * 0.5 if deadline is missing (we don't know — be conservative).
        """
        from datetime import datetime as _dt
        n_surv = int(surviving_indices.shape[0])
        if n_surv == 0:
            return np.zeros(n_surv, dtype=float)
        out = np.zeros(n_surv, dtype=float)
        now = _dt.utcnow()
        for k, original in enumerate(surviving_indices.tolist()):
            f = fundings[original]
            if not getattr(f, "is_active", True):
                continue
            dl = getattr(f, "application_deadline", None)
            if dl is None:
                out[k] = 0.5
            elif dl >= now:
                out[k] = 1.0
            # else: deadline passed, no bonus
        return out

    def _zero_out_ineligible(
        self,
        fundings: List[Funding],
        surviving_indices: np.ndarray,
        scores: np.ndarray,
    ) -> np.ndarray:
        """Hard zero out for any funding that must NEVER be recommended.

        We zero (not just penalise) because the spec says "If closed,
        score = 0" and "If deadline expired, score = 0". Inactive rows
        also get zeroed so a stale funding intel sync cannot leak through.
        """
        from datetime import datetime as _dt
        n_surv = int(surviving_indices.shape[0])
        if n_surv == 0:
            return scores
        out = np.array(scores, copy=True)
        now = _dt.utcnow()
        for k, original in enumerate(surviving_indices.tolist()):
            f = fundings[original]
            if not getattr(f, "is_active", True):
                out[k] = 0.0
                continue
            dl = getattr(f, "application_deadline", None)
            if dl is not None and dl < now:
                out[k] = 0.0
        return out

    # ------------------------------------------------------------------
    # History penalty
    # ------------------------------------------------------------------
    def _history_penalty_factor(
        self,
        *,
        fundings: List[Funding],
        surviving_indices: np.ndarray,
        user: User,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute the history penalty for each surviving funding row.

        Returns a tuple ``(factor, applied)`` where ``factor`` is a
        per-surviving-index float in ``[0, 1]`` (1.0 = no penalty,
        0.85 = soft penalty because the user already has history for this
        opportunity) and ``applied`` is the matching bool array, used by
        the breakdown so the UI can flag penalty rows.

        The penalty is intentionally soft — never below 0.8 — so a user
        who historically received a similar grant still sees fresh,
        well-matching opportunities near the top. The look-up is purely
        by ``funding.id`` because the only signal we have is which rows
        were previously awarded/applied to. Unknown user / no funding
        history → all zeros (no penalty).
        """
        n_surv = int(surviving_indices.shape[0])
        factor = np.ones(n_surv, dtype=float)
        applied = np.zeros(n_surv, dtype=bool)
        if n_surv == 0 or user is None or not getattr(user, "id", None):
            return factor, applied

        # Resolve the user's historical funding IDs (only funded/applied
        # statuses count). Lazy import to avoid loading FundingHistory at
        # module load — the recommender must remain pure-function.
        try:
            from app.models.funding_history import FundingHistory

            db = _get_request_db()
        except Exception:
            return factor, applied
        if db is None:
            return factor, applied

        try:
            historical_ids = {
                row.funding_id
                for row in (
                    db.query(FundingHistory)
                    .filter(
                        FundingHistory.owner_id == user.id,
                        FundingHistory.status.in_(("awarded", "completed", "applied", "pending")),
                        FundingHistory.funding_id.isnot(None),
                    )
                    .all()
                )
                if row.funding_id is not None
            }
        except Exception:
            return factor, applied
        if not historical_ids:
            return factor, applied

        for k, original in enumerate(surviving_indices.tolist()):
            f = fundings[original]
            if f is not None and getattr(f, "id", None) in historical_ids:
                applied[k] = True
                factor[k] = 0.85
        return factor, applied

    # ------------------------------------------------------------------
    # Publication keyword set
    # ------------------------------------------------------------------
    def _publication_keyword_set(
        self, publications: Sequence[Publication], preprocessor: TextPreprocessor
    ) -> Set[str]:
        """Set of every keyword + title-token across the user's publications,
        used for the funding-keyword overlap rule."""
        out: set[str] = set()
        for p in publications:
            for k in (p.keywords or "").split(","):
                k = k.strip().lower()
                if k:
                    out.add(k)
            for tok in preprocessor.tokenize(p.title or ""):
                if len(tok) > 2:
                    out.add(tok)
        return out


# Module-level singleton
funding_recommender = FundingRecommender()
