from collections import Counter

from app.models.research_profile import ResearchProfile


def analyze_publications(profiles):

    total_publications = sum(
        p.publications for p in profiles
    )

    total_researchers = len(profiles)

    average_publications = (
        total_publications / total_researchers
        if total_researchers
        else 0
    )

    domains = [
        p.research_domain
        for p in profiles
    ]

    top_domains = Counter(domains).most_common(5)

    organization_stats = {}

    for profile in profiles:

        organization_stats.setdefault(
            profile.organization,
            0
        )

        organization_stats[
            profile.organization
        ] += profile.publications

    return {

        "total_researchers": total_researchers,

        "total_publications": total_publications,

        "average_publications": round(
            average_publications,
            2
        ),

        "top_domains": top_domains,

        "organization_publications": organization_stats

    }