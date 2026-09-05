"""
Grant success prediction service.

Loads the RandomForestClassifier trained in app/ml/train_model.py and
uses it to estimate the probability that a researcher's profile would
be a strong match for a given funding opportunity.

Features (in this exact order, matching training):
  [publications_count, patents_count, domains_count, keywords_count,
   technology_areas_count, innovation_score, text_similarity]

text_similarity is computed with TF-IDF + cosine similarity (via
scikit-learn, already a dependency) between the researcher's combined
profile text and the funding opportunity's combined text — a fast,
lightweight alternative to embedding models that needs no extra
heavyweight downloads (e.g. PyTorch) to install or run.
"""
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.crud.publication import get_publications_by_profile
from app.crud.patent import get_patents_by_profile
from app.crud.innovation import get_innovation_score

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "grant_model.pkl")

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def _count_csv(value: str) -> int:
    if not value:
        return 0
    return len([v for v in value.split(",") if v.strip()])


def _text_similarity(profile_text: str, funding_text: str) -> float:
    profile_text = (profile_text or "").strip()
    funding_text = (funding_text or "").strip()
    if not profile_text or not funding_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([profile_text, funding_text])
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(similarity), 4)
    except ValueError:
        # Happens if both texts are only stop-words / empty after vectorizing
        return 0.0


def predict_grant_success(db, profile, funding):
    """
    Returns a dict with the predicted success probability (0-100) and
    the underlying feature values, for transparency (paired well with
    the Explanation Service).
    """
    publications = get_publications_by_profile(db, profile.id)
    patents = get_patents_by_profile(db, profile.id)

    domains_count = _count_csv(profile.research_domains)
    keywords_count = _count_csv(profile.keywords)
    tech_areas_count = _count_csv(profile.technology_areas)

    score_data = get_innovation_score(db, profile)
    innovation_score = score_data.get("innovation_score", 0)

    profile_text = " ".join(filter(None, [
        profile.research_domains,
        profile.keywords,
        profile.technology_areas,
        " ".join(p.title for p in publications if p.title),
    ]))
    funding_text = " ".join(filter(None, [
        funding.title,
        funding.domains,
        funding.description,
    ]))
    similarity = _text_similarity(profile_text, funding_text)

    features = [[
        len(publications),
        len(patents),
        domains_count,
        keywords_count,
        tech_areas_count,
        innovation_score,
        similarity,
    ]]

    model = _get_model()
    probability = model.predict_proba(features)[0][1]  # probability of class "1" (high success)
    success_percentage = round(probability * 100, 1)

    if success_percentage >= 70:
        rating = "Strong Match"
    elif success_percentage >= 40:
        rating = "Moderate Match"
    else:
        rating = "Low Match"

    return {
        "funding_id": funding.id,
        "funding_title": funding.title,
        "success_probability": success_percentage,
        "rating": rating,
        "features": {
            "publications_count": len(publications),
            "patents_count": len(patents),
            "domains_count": domains_count,
            "keywords_count": keywords_count,
            "technology_areas_count": tech_areas_count,
            "innovation_score": innovation_score,
            "text_similarity": similarity,
        },
    }