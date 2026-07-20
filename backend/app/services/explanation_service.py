def generate_explanation(
    innovation_score,
    similarity,
    publication_count,
    patent_count,
    domain_count
):

    reasons = []

    strengths = []

    improvements = []

    if similarity >= 0.80:
        reasons.append(
            "Excellent alignment with the funding opportunity."
        )
        strengths.append(
            "High semantic similarity."
        )

    elif similarity >= 0.60:
        reasons.append(
            "Good research alignment."
        )

    else:
        improvements.append(
            "Research interests can be aligned more closely with this funding."
        )

    if innovation_score >= 80:
        strengths.append(
            "Strong innovation profile."
        )
    else:
        improvements.append(
            "Increase publications and patents."
        )

    if publication_count >= 10:
        strengths.append(
            "Excellent publication record."
        )

    elif publication_count < 5:
        improvements.append(
            "Publish more research articles."
        )

    if patent_count >= 2:
        strengths.append(
            "Patent portfolio strengthens your profile."
        )

    if domain_count < 2:
        improvements.append(
            "Expand research domains."
        )

    confidence = "Low"

    if similarity >= 0.80 and innovation_score >= 80:
        confidence = "High"

    elif similarity >= 0.60:
        confidence = "Medium"

    return {
        "confidence": confidence,
        "strengths": strengths,
        "improvements": improvements,
        "summary": reasons
    }