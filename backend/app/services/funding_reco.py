import re
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_STOPWORDS = {
    "all", "disciplines", "research", "science", "sciences", "technology",
    "tech", "innovation", "development", "fundamental", "basic", "general",
    "program", "programs", "fund", "funding", "grant", "grants", "project",
    "and", "the", "for", "of", "in", "to",
}


def _term_words(term: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", term.lower())
            if len(w) >= 2 and w not in _STOPWORDS}


def build_profile_text(profile, publications) -> str:
    parts = []
    if profile is not None:
        parts += profile.research_domains or []
        parts += profile.keywords or []
        parts += profile.technology_areas or []
        if profile.headline:
            parts.append(profile.headline)
        if profile.bio:
            parts.append(profile.bio)
    parts += [p.title for p in (publications or []) if p.title]
    return " ".join(parts).strip()


def profile_terms(profile) -> set[str]:
    if profile is None:
        return set()
    terms = (profile.research_domains or []) + (profile.keywords or []) + \
            (profile.technology_areas or [])
    return {t.strip().lower() for t in terms if t.strip()}


def _opportunity_text(opp) -> str:
    return " ".join([
        opp.title or "", opp.description or "",
        " ".join(opp.domains or []), " ".join(opp.keywords or []),
    ]).strip()


def check_eligibility(opp, user_role: str, user_country: str | None,
                      today: date) -> tuple[bool, list[str]]:
    eligible = True
    reasons = []

    roles = opp.eligible_roles or []
    if roles and user_role not in roles:
        eligible = False
        reasons.append(f"Restricted to: {', '.join(roles)}")
    else:
        reasons.append("Open to your role")

    countries = [c.lower() for c in (opp.countries or [])]
    if countries and "any" not in countries:
        if user_country and user_country.strip().lower() in countries:
            reasons.append(f"Available in {user_country}")
        elif user_country:
            eligible = False
            reasons.append(f"Restricted to: {', '.join(opp.countries)}")
        else:
            reasons.append(f"Location-restricted ({', '.join(opp.countries)}); "
                           "set your country to confirm")
    else:
        reasons.append("No location restriction")

    if opp.deadline and opp.deadline < today:
        eligible = False
        reasons.append(f"Deadline passed ({opp.deadline.isoformat()})")
    elif opp.deadline:
        reasons.append(f"Deadline {opp.deadline.isoformat()}")

    return eligible, reasons


def rank_opportunities(profile, publications, user_role, user_country,
                       opportunities, today=None) -> list[dict]:
    if today is None:
        today = date.today()
    if not opportunities:
        return []

    ptext = build_profile_text(profile, publications)
    pterms = profile_terms(profile)
    pwords = set()
    for t in pterms:
        pwords |= _term_words(t)
    opp_texts = [_opportunity_text(o) for o in opportunities]

    cosines = [0.0] * len(opportunities)
    if ptext:
        try:
            matrix = TfidfVectorizer(stop_words="english").fit_transform([ptext] + opp_texts)
            cosines = list(cosine_similarity(matrix[0:1], matrix[1:]).flatten())
        except ValueError:
            pass

    results = []
    for opp, cos in zip(opportunities, cosines):
        eligible, reasons = check_eligibility(opp, user_role, user_country, today)
        opp_terms = {t.strip().lower() for t in
                     (opp.domains or []) + (opp.keywords or []) if t.strip()}
        matched = sorted(t for t in opp_terms if _term_words(t) & pwords)

        tag_ratio = len(matched) / max(1, len(opp_terms))
        text_sim = min(1.0, float(cos) * 4)
        relevance = round(100 * (0.6 * tag_ratio + 0.4 * text_sim), 1)

        results.append({
            "opportunity": opp,
            "relevance_score": relevance,
            "eligible": eligible,
            "matched_terms": matched,
            "reasons": reasons,
        })

    results.sort(key=lambda r: (
        not r["eligible"],
        -r["relevance_score"],
        r["opportunity"].deadline or date.max,
    ))
    return results
