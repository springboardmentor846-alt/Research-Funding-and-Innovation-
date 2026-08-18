"""Quality layer for the patent module: normalization, dedup, validation."""
from app.patents.quality.normalization import (
    normalize_patent_record,
    normalize_patent_number,
    detect_technology_area,
    detect_country,
    split_inventors,
    split_keywords,
    parse_date,
)
from app.patents.quality.deduplication import (
    decide_merge,
    is_duplicate_by_number,
    is_duplicate_by_metadata,
    build_merge_fields,
    jaccard,
)
from app.patents.quality.validation import is_valid_patent_record

__all__ = [
    "normalize_patent_record",
    "normalize_patent_number",
    "detect_technology_area",
    "detect_country",
    "split_inventors",
    "split_keywords",
    "parse_date",
    "decide_merge",
    "is_duplicate_by_number",
    "is_duplicate_by_metadata",
    "build_merge_fields",
    "jaccard",
    "is_valid_patent_record",
]
