"""
AI Recommendation service.

Provides embedding-based (semantic) recommendations, as opposed to the
existing rule-based funding_sources_service matching (which filters by
exact domain-string overlap). This uses TF-IDF vectors + cosine similarity
from scikit-learn (already a project dependency for grant_prediction) to
rank items by how semantically close their text is to a researcher's
profile — so a profile mentioning "machine learning" can still match a
funding call about "artificial intelligence", which exact-substring
matching would miss.

No new tables: reads ResearchProfile / FundingOpportunity, both of which
already exist.
"""
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity
from app.models.user import User


def _profile_text(profile: ResearchProfile) -> str:
    parts = [
        profile.research_domains or "",
        profile.keywords or "",
        profile.technology_areas or "",
        profile.organization_name or "",
    ]
    return " ".join(p for p in parts if p).strip()


def _funding_text(opportunity: FundingOpportunity) -> str:
    parts = [
        opportunity.title or "",
        opportunity.description or "",
        opportunity.domains or "",
        opportunity.eligibility or "",
    ]
    return " ".join(p for p in parts if p).strip()


def recommend_funding(db: Session, profile: ResearchProfile, top_n: int = 5) -> list[dict]:
    """Rank funding opportunities by semantic similarity to a profile."""
    query_text = _profile_text(profile)
    opportunities = db.query(FundingOpportunity).all()

    if not query_text or not opportunities:
        return []

    docs = [_funding_text(o) for o in opportunities]
    corpus = [query_text] + docs
    if not any(doc.strip() for doc in docs):
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Empty vocabulary (e.g. every field was just stopwords/blank)
        return []

    profile_vector = matrix[0:1]
    opportunity_vectors = matrix[1:]
    scores = cosine_similarity(profile_vector, opportunity_vectors)[0]

    ranked = sorted(zip(opportunities, scores), key=lambda pair: pair[1], reverse=True)

    return [
        {
            "id": opportunity.id,
            "title": opportunity.title,
            "source": opportunity.source,
            "deadline": opportunity.deadline,
            "amount": opportunity.amount,
            "link": opportunity.link,
            "match_score": round(float(score), 4),
        }
        for opportunity, score in ranked[:top_n]
        if score > 0
    ]


def recommend_collaborators(db: Session, profile: ResearchProfile, top_n: int = 5) -> list[dict]:
    """Rank other researchers by semantic similarity of their profile text —
    a lightweight, embedding-based alternative to matching on exact shared
    domain tags."""
    query_text = _profile_text(profile)
    other_profiles = (
        db.query(ResearchProfile).filter(ResearchProfile.id != profile.id).all()
    )

    if not query_text or not other_profiles:
        return []

    docs = [_profile_text(p) for p in other_profiles]
    corpus = [query_text] + docs
    if not any(doc.strip() for doc in docs):
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return []

    query_vector = matrix[0:1]
    other_vectors = matrix[1:]
    scores = cosine_similarity(query_vector, other_vectors)[0]

    ranked = sorted(zip(other_profiles, scores), key=lambda pair: pair[1], reverse=True)

    results = []
    for other_profile, score in ranked[:top_n]:
        if score <= 0:
            continue
        user = db.query(User).filter(User.id == other_profile.user_id).first()
        results.append(
            {
                "user_id": other_profile.user_id,
                "name": user.name if user else None,
                "organization_name": other_profile.organization_name,
                "research_domains": other_profile.research_domains,
                "match_score": round(float(score), 4),
            }
        )
    return results