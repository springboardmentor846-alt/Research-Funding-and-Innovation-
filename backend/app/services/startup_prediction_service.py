"""
Startup funding-match prediction.

Estimates how well a startup's profile matches a given funding
opportunity, combining a TF-IDF text-similarity match score with a
profile-readiness score (how complete/investment-ready the startup
profile looks). This mirrors the researcher-side grant prediction in
spirit, adapted to startup profile fields instead of publications/patents.
"""


def _startup_text(startup) -> str:
    parts = [
        startup.industry, startup.stage, startup.funding_stage,
        startup.technology_stack, startup.research_interests,
        startup.problem_statement, startup.solution, startup.description,
    ]
    return " ".join(p for p in parts if p)


def _text_similarity(startup_text: str, funding_text: str) -> float:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    startup_text = (startup_text or "").strip()
    funding_text = (funding_text or "").strip()
    if not startup_text or not funding_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([startup_text, funding_text])
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(similarity)
    except ValueError:
        return 0.0


def _readiness_score(startup) -> int:
    readiness = 35
    if startup.stage and startup.stage.lower() not in ("idea", ""):
        readiness += 10
    if startup.funding_stage and startup.funding_stage.lower() not in ("bootstrapped", ""):
        readiness += 10
    if startup.team_size and startup.team_size >= 2:
        readiness += 8
    if startup.description:
        readiness += 7
    if startup.problem_statement and startup.solution:
        readiness += 10
    if startup.technology_stack:
        readiness += 8
    if startup.pitch_deck_url:
        readiness += 7
    return min(readiness, 100)


def _profile_completion(startup) -> int:
    fields = [
        startup.startup_name, startup.tagline, startup.industry, startup.stage,
        startup.founded_year, startup.funding_stage, startup.location,
        startup.description, startup.problem_statement, startup.solution,
        startup.technology_stack, startup.research_interests, startup.funding_needed,
        startup.team_size,
    ]
    filled = sum(1 for v in fields if v not in (None, ""))
    return round((filled / len(fields)) * 100)


def predict_startup_funding_match(startup, funding):
    startup_text = _startup_text(startup)
    funding_text = " ".join(p for p in [funding.title, funding.domains, funding.description] if p)

    similarity = _text_similarity(startup_text, funding_text)
    match_score = round(similarity * 100, 1)
    readiness = _readiness_score(startup)
    profile_completion = _profile_completion(startup)

    success_estimate = round((match_score * 0.6) + (readiness * 0.4), 1)

    strengths = []
    improvements = []

    if startup.technology_stack:
        strengths.append("A defined technology stack helps demonstrate technical capability.")
    else:
        improvements.append("Add your technology stack so the funding match can better understand your solution.")

    if startup.problem_statement and startup.solution:
        strengths.append("Your problem statement and solution provide clear product context.")
    else:
        improvements.append("Complete both the problem statement and solution to improve funding readiness.")

    if startup.team_size and startup.team_size >= 2:
        strengths.append("Your profile shows a multi-member team.")
    else:
        improvements.append("Add your team information to strengthen the readiness assessment.")

    if startup.pitch_deck_url:
        strengths.append("A pitch deck is included in the startup profile.")
    else:
        improvements.append("Add a pitch deck link if you have one available.")

    if match_score >= 70:
        strengths.append("Your startup profile has strong alignment with this funding opportunity.")
    elif match_score < 40:
        improvements.append("Review the opportunity requirements and strengthen the parts of your profile that align with them.")

    return {
        "funding_id": funding.id,
        "funding_title": funding.title,
        "success_estimate": success_estimate,
        "match_score": match_score,
        "readiness_score": readiness,
        "profile_completion": profile_completion,
        "strengths": strengths[:5],
        "improvements": improvements[:5],
        "summary": (
            "This estimate combines text similarity between your startup and the funding "
            "opportunity with your current profile completeness and readiness. It is a "
            "decision-support estimate, not a guarantee of funding success."
        ),
    }