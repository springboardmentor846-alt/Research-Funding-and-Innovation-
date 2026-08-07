from collections import Counter


def generate_intelligence(

    profile,

    recommendations,

    grant_matches,

    profiles

):

    domains = [

        p.research_domain

        for p in profiles

    ]

    organizations = [

        p.organization

        for p in profiles

    ]

    total_publications = sum(

        p.publications

        for p in profiles

    )

    total_patents = sum(

        p.patents

        for p in profiles

    )

    top_domain = Counter(

        domains

    ).most_common(1)

    top_org = Counter(

        organizations

    ).most_common(3)

    best_grant = None

    if grant_matches:

        best_grant = max(

            grant_matches,

            key=lambda x: x["match_score"]

        )

    return {

        "researcher": profile.user.full_name,

        "research_domain": profile.research_domain,

        "technology_area": profile.technology_area,

        "organization": profile.organization,

        "publications": profile.publications,

        "patents": profile.patents,

        "experience": profile.experience,

        "recommended_funding": len(

            recommendations

        ),

        "best_grant": best_grant,

        "total_publications": total_publications,

        "total_patents": total_patents,

        "top_research_domain": top_domain,

        "top_organizations": top_org

    }