"""Unit tests for patent normalization, dedup, and validation.

Run with: ``pytest backend/tests/test_patents_normalization.py``
"""
from datetime import datetime

import pytest

from app.patents.quality import (
    normalize_patent_record,
    normalize_patent_number,
    detect_technology_area,
    detect_country,
    split_inventors,
    split_keywords,
    parse_date,
    decide_merge,
    is_valid_patent_record,
)


# ---------------------------------------------------------------------------
# normalize_patent_number
# ---------------------------------------------------------------------------


class TestNormalizePatentNumber:
    def test_canonicalizes_separators(self):
        assert normalize_patent_number("us 10,123,456 b2") == "US10123456B2"
        assert normalize_patent_number("US-10123456-B2") == "US10123456B2"
        assert normalize_patent_number("ep 3 456 789 a1") == "EP3456789A1"

    def test_empty(self):
        assert normalize_patent_number("") == ""
        assert normalize_patent_number(None) == ""  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestSplitInventors:
    def test_splits_comma(self):
        assert split_inventors("Doe, John; Roe, Jane") == "Doe, John, Roe, Jane"

    def test_splits_pipe(self):
        assert split_inventors("Doe | Roe") == "Doe, Roe"

    def test_empty(self):
        assert split_inventors("") is None
        assert split_inventors(None) is None


class TestSplitKeywords:
    def test_basic(self):
        assert split_keywords("ai, ml, nlp") == "ai, ml, nlp"

    def test_empty(self):
        assert split_keywords("") is None


class TestParseDate:
    def test_iso(self):
        assert parse_date("2023-04-01") == datetime(2023, 4, 1)

    def test_iso_with_z(self):
        d = parse_date("2023-04-01T00:00:00Z")
        assert d is not None
        assert d.year == 2023 and d.month == 4 and d.day == 1

    def test_none(self):
        assert parse_date(None) is None
        assert parse_date("") is None
        assert parse_date("not a date") is None

    def test_datetime_passthrough(self):
        now = datetime.utcnow()
        assert parse_date(now) is now


class TestDetectTechnologyArea:
    def test_known_prefix(self):
        assert detect_technology_area("G06N3/04") == "Computing & AI"
        assert detect_technology_area("A61K") == "Medical & Health"
        assert detect_technology_area("H04L29/06") == "Telecommunications"

    def test_unknown(self):
        assert detect_technology_area("Z99X") is None
        assert detect_technology_area(None) is None


class TestDetectCountry:
    def test_known_prefixes(self):
        assert detect_country("US10123456B2") == "US"
        assert detect_country("EP3456789A1") == "EP"
        assert detect_country("WO2023000001A1") == "WO"
        assert detect_country("JP2023000001A") == "JP"

    def test_unknown(self):
        assert detect_country("XX12345") is None
        assert detect_country("") is None


# ---------------------------------------------------------------------------
# normalize_patent_record
# ---------------------------------------------------------------------------


def _raw_google_patent() -> dict:
    return {
        "publication_number": "US 11,123,456 B2",
        "title": "  Attention-based medical image segmentation  ",
        "abstract": "A neural network for segmenting tumors in MRI scans.",
        "inventors": "Doe, John; Roe, Jane",
        "assignee": "Acme Health",
        "country": "US",
        "cpc": "G06N3/045",
        "pub_date": "2023-04-01",
        "date_filed": "2022-09-15",
        "cited_by_count": 47,
        "url": "https://patents.google.com/patent/US11123456B2",
        "keywords": "neural network, MRI, segmentation",
    }


class TestNormalizePatentRecord:
    def test_basic_normalization(self):
        out = normalize_patent_record(_raw_google_patent(), source="google_patents")
        assert out["patent_number"] == "US11123456B2"
        assert out["title"] == "Attention-based medical image segmentation"
        assert out["assignee"] == "Acme Health"
        assert out["country"] == "US"
        assert out["classification"] == "G06N3/045"
        assert out["technology_area"] == "Computing & AI"
        assert out["citations"] == 47
        assert out["publication_year"] == 2023
        assert out["filing_date"] == datetime(2022, 9, 15)
        assert out["publication_date"] == datetime(2023, 4, 1)
        assert out["source"] == "google_patents"
        assert out["inventors"] == "Doe, John, Roe, Jane"
        assert out["keywords"] == "neural network, MRI, segmentation"

    def test_unknown_source_raises(self):
        with pytest.raises(ValueError):
            normalize_patent_record(_raw_google_patent(), source="bogus")

    def test_assignee_list(self):
        raw = {
            "publication_number": "EP3456789A1",
            "title": "Solid-state battery",
            "abstract": "Novel solid electrolyte for Li-S batteries.",
            "applicant": ["Innolith AG"],
            "cpc": "H01M10/0562",
            "pub_date": "2024-01-15",
        }
        out = normalize_patent_record(raw, source="the_lens")
        assert out["assignee"] == "Innolith AG"
        assert out["technology_area"] == "Electronics & Semiconductors"
        assert out["country"] == "EP"

    def test_publication_year_fallback(self):
        raw = {
            "patent_number": "US9999999B2",
            "title": "Foo",
            "abstract": "Bar",
            "pub_date": "2020-06-01",
        }
        out = normalize_patent_record(raw, source="uspto")
        assert out["publication_year"] == 2020
        assert out["filing_date"] is None


class TestIsValidPatentRecord:
    def test_valid(self):
        ok, _ = is_valid_patent_record(
            {"patent_number": "US1", "title": "Foo", "abstract": "Bar"}
        )
        assert ok

    def test_valid_keywords_only(self):
        ok, _ = is_valid_patent_record(
            {"patent_number": "US1", "title": "Foo", "keywords": "ai, ml"}
        )
        assert ok

    def test_missing_number(self):
        ok, reason = is_valid_patent_record({"title": "Foo", "abstract": "Bar"})
        assert not ok
        assert "patent_number" in reason

    def test_missing_title(self):
        ok, reason = is_valid_patent_record({"patent_number": "US1", "abstract": "Bar"})
        assert not ok
        assert "title" in reason

    def test_missing_both_abstract_and_keywords(self):
        ok, reason = is_valid_patent_record({"patent_number": "US1", "title": "Foo"})
        assert not ok
        assert "abstract" in reason


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------


class TestDedup:
    def test_exact_patent_number_is_duplicate(self):
        a = {"patent_number": "US11123456B2", "title": "Foo", "citations": 5}
        b = {"patent_number": "US11123456B2", "title": "Foo bar", "citations": 7}
        decision = decide_merge(incoming=b, existing=a)
        assert decision.is_duplicate
        assert decision.matched_field == "patent_number"
        # Merge picks the new citation count (incoming wins when non-empty)
        assert decision.merge_fields["citations"] == 7

    def test_title_similarity_duplicate(self):
        a = {
            "patent_number": "US11123456B2",
            "title": "Attention-based medical image segmentation",
            "assignee": "Acme",
            "inventors": "Doe, John",
        }
        b = {
            "patent_number": "US9999999B2",  # different number, cross-source
            "title": "Attention-based medical image segmentation using neural networks",
            "assignee": "Acme Inc",
            "inventors": "Doe, John",
        }
        decision = decide_merge(incoming=b, existing=a)
        assert decision.is_duplicate
        assert decision.matched_field in {"title", "assignee+inventor"}

    def test_different_patents(self):
        a = {
            "patent_number": "US11123456B2",
            "title": "Solid-state battery",
            "assignee": "Innolith",
            "inventors": "Schmidt",
        }
        b = {
            "patent_number": "US9999999B2",
            "title": "Quantum error correction",
            "assignee": "IBM",
            "inventors": "Smith",
        }
        decision = decide_merge(incoming=b, existing=a)
        assert not decision.is_duplicate
