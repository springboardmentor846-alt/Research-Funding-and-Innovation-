import requests
import pycountry
from collections import Counter

OPENALEX_URL = "https://api.openalex.org/works"


def get_country_name(code):
    if not code:
        return "Unknown"

    country = pycountry.countries.get(alpha_2=code.upper())
    return country.name if country else code


def fetch_openalex(query: str):
    params = {
        "search": query,
        "per-page": 100
    }

    response = requests.get(
        OPENALEX_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def publication_trend(data):

    yearly_counts = Counter()

    works = data.get("results", [])

    for work in works:
        year = work.get("publication_year")

        if year:
            yearly_counts[year] += 1

    trend = []

    for year in sorted(yearly_counts.keys()):
        trend.append({
            "year": year,
            "count": yearly_counts[year]
        })

    return trend


def country_statistics(data):

    country_counter = Counter()

    works = data.get("results", [])

    for work in works:

        authorships = work.get("authorships", [])

        seen = set()

        for author in authorships:

            institutions = author.get("institutions", [])

            for institution in institutions:

                country = institution.get("country_code")

                if country and country not in seen:
                    country_counter[country] += 1
                    seen.add(country)

    countries = []

    for code, count in country_counter.most_common(10):

        countries.append({
            "country": get_country_name(code),
            "count": count
        })

    return countries


def university_statistics(data):

    university_counter = Counter()

    works = data.get("results", [])

    for work in works:

        authorships = work.get("authorships", [])

        seen = set()

        for author in authorships:

            institutions = author.get("institutions", [])

            for institution in institutions:

                name = institution.get("display_name")

                if name and name not in seen:
                    university_counter[name] += 1
                    seen.add(name)

    universities = []

    for name, count in university_counter.most_common(10):

        universities.append({
            "university": name,
            "count": count
        })

    return universities

from collections import Counter


def topic_graph(data):

    works = data.get("results", [])

    concept_counter = Counter()

    # Count concept frequency
    for work in works:
        for concept in work.get("concepts", []):
            name = concept.get("display_name")

            if name:
                concept_counter[name] += 1

    # Keep only top 20 concepts
    top_concepts = {
        name
        for name, _ in concept_counter.most_common(20)
    }

    nodes = [
        {
            "id": concept,
            "label": concept
        }
        for concept in sorted(top_concepts)
    ]

    edge_counter = Counter()

    for work in works:

        concepts = [
            c["display_name"]
            for c in work.get("concepts", [])
            if c.get("display_name") in top_concepts
        ]

        concepts = list(set(concepts))

        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                edge_counter[(concepts[i], concepts[j])] += 1

    edges = []

    for (src, dst), weight in edge_counter.items():

        if weight >= 2:          # keep only stronger connections
            edges.append({
                "source": src,
                "target": dst
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


def ai_insight(query, trend, countries, universities):

    total_publications = sum(item["count"] for item in trend)

    latest_year = (
        max(trend, key=lambda x: x["year"])["year"]
        if trend else "N/A"
    )

    top_country = (
        countries[0]["country"]
        if countries else "Unknown"
    )

    top_university = (
        universities[0]["university"]
        if universities else "Unknown"
    )

    insight = (
        f'Research on "{query}" returned approximately '
        f'{total_publications} publications in the retrieved dataset. '
        f'The latest publication year is {latest_year}. '
        f'The leading contributing country is {top_country}, '
        f'while the most active institution is {top_university}. '
        f'This topic demonstrates active international research collaboration '
        f'and continued academic interest.'
    )

    return insight