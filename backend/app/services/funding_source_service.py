def collect_funding_sources():

    opportunities = []

    opportunities.extend(
        collect_government_grants()
    )

    opportunities.extend(
        collect_research_council_grants()
    )

    opportunities.extend(
        collect_innovation_funds()
    )

    opportunities.extend(
        collect_international_funding()
    )

    return opportunities


def collect_government_grants():

    """
    Government grant source adapter.

    Actual external funding API / dataset
    integration will be connected here.
    """

    return []


def collect_research_council_grants():

    """
    Research council funding adapter.

    Examples:
    ANRF, DST, DBT, NSF, NIH, etc.

    Actual API/dataset integrations
    will be connected here.
    """

    return []


def collect_innovation_funds():

    """
    Innovation and startup funding
    source adapter.
    """

    return []


def collect_international_funding():

    """
    International funding source adapter.

    Examples:
    Horizon Europe,
    Wellcome,
    international research programs, etc.
    """

    return []