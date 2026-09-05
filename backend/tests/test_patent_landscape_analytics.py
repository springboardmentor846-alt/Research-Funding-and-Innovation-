from app.services.patent_landscape_service import (
    build_researcher_text,
    calculate_similarity,
    extract_top_topics,
    JURISDICTION_NAMES,
    CPC_SECTIONS,
)


class FakeProfile:
    def __init__(self, research_domains="", keywords="", technology_areas="", organization_name=""):
        self.research_domains = research_domains
        self.keywords = keywords
        self.technology_areas = technology_areas
        self.organization_name = organization_name


class FakePublication:
    def __init__(self, title):
        self.title = title


def test_build_researcher_text_combines_all_profile_fields():
    profile = FakeProfile(
        research_domains="AI, Robotics",
        keywords="machine learning",
        technology_areas="Neural Networks",
        organization_name="Test University",
    )
    publications = [FakePublication("A study on robotics")]

    text = build_researcher_text(profile, publications)

    assert "AI, Robotics" in text
    assert "machine learning" in text
    assert "Neural Networks" in text
    assert "Test University" in text
    assert "A study on robotics" in text


def test_build_researcher_text_handles_no_profile():
    text = build_researcher_text(None, [])
    assert text == ""


def test_calculate_similarity_high_for_overlapping_text():
    similarity = calculate_similarity("AI robotics machine learning", "robotics machine learning patent")
    assert similarity > 0.3


def test_calculate_similarity_zero_for_empty_text():
    assert calculate_similarity("", "something") == 0.0
    assert calculate_similarity("something", "") == 0.0


def test_extract_top_topics_from_fake_lens_patents():
    fake_patents = [
        {"biblio": {"invention_title": [{"lang": "en", "text": "Battery cooling system"}]}},
        {"biblio": {"invention_title": [{"lang": "en", "text": "Battery thermal management"}]}},
    ]
    topics = extract_top_topics(fake_patents)
    topic_words = [t["topic"] for t in topics]
    assert "battery" in topic_words


def test_jurisdiction_and_cpc_reference_tables_are_populated():
    assert JURISDICTION_NAMES["US"] == "United States"
    assert JURISDICTION_NAMES["IN"] == "India"
    assert CPC_SECTIONS["G"] == "Physics"
    assert CPC_SECTIONS["H"] == "Electricity"