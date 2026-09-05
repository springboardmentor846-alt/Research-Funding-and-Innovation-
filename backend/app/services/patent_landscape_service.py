"""
Global Patent Landscape service.

Runs a live search against Lens.org for a query, then builds analytics
over the results: jurisdiction distribution, filing trends, top
applicants, CPC technology classes/clusters, top topics, and a
personalized relevance ranking (TF-IDF similarity between the current
researcher's profile and each patent's title/abstract/CPC codes).
"""
import re
from collections import Counter

from app.services.lens_service import search_patents

JURISDICTION_NAMES = {
    "US": "United States", "CN": "China", "JP": "Japan", "KR": "South Korea",
    "IN": "India", "GB": "United Kingdom", "DE": "Germany", "FR": "France",
    "CA": "Canada", "AU": "Australia", "RU": "Russia", "TW": "Taiwan",
    "ZA": "South Africa", "BR": "Brazil", "MX": "Mexico", "SG": "Singapore",
    "NZ": "New Zealand", "IT": "Italy", "ES": "Spain", "NL": "Netherlands",
    "SE": "Sweden", "CH": "Switzerland", "AT": "Austria", "BE": "Belgium",
    "DK": "Denmark", "FI": "Finland", "NO": "Norway",
    "WO": "WIPO / International", "EP": "European Patent Office",
}

CPC_SECTIONS = {
    "A": "Human Necessities",
    "B": "Performing Operations & Transporting",
    "C": "Chemistry & Metallurgy",
    "D": "Textiles & Paper",
    "E": "Fixed Constructions",
    "F": "Mechanical Engineering",
    "G": "Physics",
    "H": "Electricity",
    "Y": "Emerging / Cross-sectional Technologies",
}

TOPIC_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "using",
    "based", "method", "system", "apparatus", "device", "process",
    "data", "information", "technology", "application", "applications",
    "one", "new", "provided", "configured", "including", "thereof",
    "into", "over", "under", "between", "through", "such", "may",
    "can", "are", "was", "were", "has", "have", "having", "their",
    "which", "where", "patent", "invention", "embodiment", "embodiments",
    "present", "disclosed", "methodology", "according", "claim", "claims",
}


def build_researcher_text(profile, publications):
    parts = []
    if profile:
        if profile.research_domains:
            parts.append(profile.research_domains)
        if profile.keywords:
            parts.append(profile.keywords)
        if profile.technology_areas:
            parts.append(profile.technology_areas)
        if profile.organization_name:
            parts.append(profile.organization_name)
    for pub in publications or []:
        if pub.title:
            parts.append(pub.title)
    return " ".join(parts)


def calculate_similarity(researcher_text: str, patent_text: str) -> float:
    # Imported lazily so scikit-learn is only loaded when this feature is used.
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    if not researcher_text or not patent_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform([researcher_text, patent_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(similarity)
    except ValueError:
        return 0.0


def _extract_text_field(data):
    """Lens sometimes returns a string, a dict, or a list of {lang, text} dicts."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        return data.get("text") or data.get("value") or ""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lang = item.get("lang") or item.get("language")
                text = item.get("text") or item.get("value")
                if lang == "en" and text:
                    return text
        for item in data:
            if isinstance(item, dict):
                text = item.get("text") or item.get("value")
                if text:
                    return text
    return ""


def extract_top_topics(patents, limit=10):
    counter = Counter()
    for patent in patents or []:
        biblio = patent.get("biblio") or {}
        title = _extract_text_field(biblio.get("invention_title") or patent.get("title") or "")
        abstract = _extract_text_field(biblio.get("abstract") or patent.get("abstract") or "")

        text = f"{title} {abstract}".lower()
        words = re.findall(r"[a-z][a-z0-9+#.-]{2,}", text)
        for word in words:
            word = word.strip(".-")
            if len(word) < 3 or word in TOPIC_STOPWORDS or word.isdigit():
                continue
            counter[word] += 1

    return [{"topic": word.replace("-", " "), "count": count} for word, count in counter.most_common(limit)]


def patent_landscape(query: str, profile, publications):
    researcher_text = build_researcher_text(profile, publications)

    response = search_patents(query=query, size=100)
    patents = response.get("data", [])

    jurisdiction_counter = Counter()
    status_counter = Counter()
    year_counter = Counter()
    applicant_counter = Counter()
    cpc_counter = Counter()
    cluster_counter = Counter()

    relevant_patents = []

    for patent in patents:
        jurisdiction = patent.get("jurisdiction")
        if jurisdiction:
            jurisdiction_counter[jurisdiction] += 1

        legal = patent.get("legal_status") or {}
        status = legal.get("patent_status")
        if status:
            status_counter[status] += 1

        biblio = patent.get("biblio") or {}

        publication_reference = biblio.get("publication_reference") or {}
        publication_number = publication_reference.get("doc_number") or publication_reference.get("document_id")
        publication_date = publication_reference.get("date")
        if publication_date:
            year_counter[publication_date[:4]] += 1

        parties = biblio.get("parties") or {}
        applicants_data = parties.get("applicants") or []
        patent_applicants = []
        for applicant in applicants_data:
            applicant_name = (applicant.get("extracted_name") or {}).get("value")
            if applicant_name:
                applicant_counter[applicant_name] += 1
                patent_applicants.append(applicant_name)

        classifications_cpc = biblio.get("classifications_cpc") or {}
        classifications = classifications_cpc.get("classifications") or []
        patent_cpcs = []
        for classification in classifications:
            symbol = classification.get("symbol")
            if symbol:
                cpc_counter[symbol] += 1
                patent_cpcs.append(symbol)
                section_name = CPC_SECTIONS.get(symbol[0], "Other Technologies")
                cluster_counter[section_name] += 1

        title = _extract_text_field(biblio.get("invention_title") or "")
        abstract_text = _extract_text_field(biblio.get("abstract") or patent.get("abstract") or "")

        patent_text = " ".join(filter(None, [title, abstract_text] + patent_cpcs))

        similarity = calculate_similarity(researcher_text, patent_text) if researcher_text and patent_text else 0.0
        relevance_score = round(similarity * 100, 2)

        relevant_patents.append({
            "title": title or "Title unavailable",
            "publication_number": publication_number,
            "publication_date": publication_date,
            "jurisdiction": jurisdiction,
            "jurisdiction_name": JURISDICTION_NAMES.get(jurisdiction, jurisdiction) if jurisdiction else None,
            "applicants": patent_applicants[:3],
            "cpc_codes": patent_cpcs[:5],
            "status": status,
            "relevance_score": relevance_score,
        })

    relevant_patents.sort(key=lambda item: item["relevance_score"], reverse=True)

    jurisdiction_distribution = [
        {"code": code, "name": JURISDICTION_NAMES.get(code, code), "count": count}
        for code, count in jurisdiction_counter.most_common(10)
    ]

    insights = []
    if jurisdiction_counter:
        top_code = jurisdiction_counter.most_common(1)[0][0]
        insights.append(f"Top patent filing jurisdiction: {JURISDICTION_NAMES.get(top_code, top_code)} ({top_code})")
    if applicant_counter:
        insights.append(f"Most active organization: {applicant_counter.most_common(1)[0][0]}")
    if cpc_counter:
        insights.append(f"Most common CPC class: {cpc_counter.most_common(1)[0][0]}")

    total_cluster_occurrences = sum(cluster_counter.values())
    innovation_map = [
        {
            "technology_cluster": cluster,
            "classification_occurrences": count,
            "share_percentage": round((count / total_cluster_occurrences) * 100, 2) if total_cluster_occurrences else 0,
        }
        for cluster, count in cluster_counter.most_common()
    ]

    return {
        "query": query,
        "personalized_relevance": bool(researcher_text.strip()),
        "summary": {
            "total_patents": len(patents),
            "countries": len(jurisdiction_counter),
            "organizations": len(applicant_counter),
            "technology_classes": len(cpc_counter),
        },
        "country_distribution": jurisdiction_distribution,
        "status_distribution": dict(status_counter),
        "filing_trends": dict(sorted(year_counter.items())),
        "top_applicants": dict(applicant_counter.most_common(10)),
        "technology_classes": dict(cpc_counter.most_common(10)),
        "patent_clusters": dict(cluster_counter.most_common()),
        "relevant_patents": relevant_patents[:20],
        "innovation_map": innovation_map,
        "top_topics": extract_top_topics(patents),
        "insights": insights,
    }