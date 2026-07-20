from sklearn.metrics.pairwise import cosine_similarity

from app.ai.embedding import generate_embedding


def calculate_similarity(
    researcher_text: str,
    funding_text: str
) -> float:
    """
    Returns cosine similarity between researcher profile
    and funding opportunity.
    """

    researcher_vector = generate_embedding(
        researcher_text
    ).reshape(1, -1)

    funding_vector = generate_embedding(
        funding_text
    ).reshape(1, -1)

    similarity = cosine_similarity(
        researcher_vector,
        funding_vector
    )[0][0]

    return float(similarity)