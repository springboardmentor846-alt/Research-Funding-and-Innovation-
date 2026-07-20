from app.ai.recommendation import calculate_similarity


def build_researcher_text(
    profile,
    domains,
    keywords,
    technologies,
):
    """
    Converts researcher profile into a single text
    for semantic embedding.
    """

    return f"""
Qualification: {profile.highest_qualification or ""}

Current Position: {profile.current_position or ""}

Organization: {profile.organization_name or ""}

Bio:
{profile.bio or ""}

Research Domains:
{" ".join(domain.name for domain in domains)}

Keywords:
{" ".join(keyword.name for keyword in keywords)}

Technology Areas:
{" ".join(tech.name for tech in technologies)}
"""


def build_funding_text(funding):
    """
    Converts funding opportunity into text.
    """

    return f"""
Title:
{funding.title or ""}

Organization:
{funding.organization or ""}

Research Domain:
{funding.research_domain or ""}

Description:
{funding.description or ""}

Keywords:
{funding.keywords or ""}
"""


def build_publication_text(publication):
    """
    Converts publication into text.
    """

    return f"""
Title:
{publication.title or ""}

Publication Type:
{publication.publication_type or ""}

Authors:
{publication.authors or ""}

Journal:
{publication.journal_or_conference or ""}

Publisher:
{publication.publisher or ""}

Abstract:
{publication.abstract or ""}
"""


def build_patent_text(patent):
    """
    Converts patent into text.
    """

    return f"""
Title:
{patent.title or ""}

Patent Number:
{patent.patent_number or ""}

Inventors:
{patent.inventors or ""}

Patent Office:
{patent.patent_office or ""}

Status:
{patent.status or ""}

Description:
{patent.description or ""}
"""


def rank_recommendations(
    researcher_text,
    items,
    text_builder,
    id_field="id",
    subtitle_field=None,
):
    """
    Generic semantic ranking engine.
    """

    recommendations = []

    for item in items:

        item_text = text_builder(item)

        similarity = calculate_similarity(
            researcher_text,
            item_text
        )

        recommendation = {
            "id": getattr(item, id_field),
            "title": getattr(item, "title"),
            "similarity_score": round(
                similarity,
                4
            )
        }

        if subtitle_field:
            recommendation["subtitle"] = getattr(
                item,
                subtitle_field,
                None
            )

        recommendations.append(
            recommendation
        )

    recommendations.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return recommendations