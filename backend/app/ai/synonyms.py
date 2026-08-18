"""Semantic keyword expansion for research interest matching.

Each entry is a *group* of terms that should be considered semantically
related for the purpose of the funding recommender. Given any user-supplied
interest (e.g. "Cybersecurity"), ``expand_terms`` returns the union of every
synonym group that contains a normalized form of that interest, so downstream
code can treat "Network Security", "Malware", "Zero Trust", etc. as related
to "Cybersecurity" without requiring an LLM call.

This is intentionally a static map rather than a learned embedding: the
recommender needs to be deterministic, debuggable, and fast (no network
round-trips). New groups can be added without code changes elsewhere; the
recommender just consumes the flat set of expanded tokens.
"""
from __future__ import annotations

import re
from typing import Iterable


# Each group is a set of related terms. Comparison is case-insensitive and
# ignores simple punctuation, so "Cyber Security" matches "cybersecurity"
# and "zero-trust" matches "zero trust".
SYNONYM_GROUPS: list[set[str]] = [
    # --- Cybersecurity ---
    {
        "cyber security", "cybersecurity", "information security",
        "infosec", "network security", "cloud security", "zero trust",
        "digital forensics", "digital security", "threat intelligence",
        "threat detection", "malware", "malware analysis", "ransomware",
        "phishing", "cryptography", "encryption", "penetration testing",
        "ethical hacking", "intrusion detection", "vulnerability",
        "security", "secure computing", "privacy", "cybersafety",
        "cyber defense", "cyber attack", "ddos", "botnet", "siem",
    },
    # --- AI / ML ---
    {
        "artificial intelligence", "machine learning", "deep learning",
        "nlp", "natural language processing", "computer vision",
        "generative ai", "neural network", "neural networks",
        "reinforcement learning", "ai", "ml", "llm", "large language model",
        "transformer", "foundation model", "transfer learning",
        "data mining", "pattern recognition", "ai safety", "agentic ai",
        "federated learning", "explainable ai", "xai",
    },
    # --- Data Science / Big Data ---
    {
        "data science", "data analytics", "big data", "data engineering",
        "statistics", "statistical learning", "predictive modeling",
        "knowledge discovery", "data visualization",
    },
    # --- Cloud / Distributed systems ---
    {
        "cloud computing", "distributed systems", "edge computing",
        "serverless", "microservices", "devops", "kubernetes",
    },
    # --- IoT / Embedded ---
    {
        "internet of things", "iot", "embedded systems", "sensor networks",
        "cyber physical systems", "wearables",
    },
    # --- Robotics / Control ---
    {
        "robotics", "autonomous systems", "control systems", "drone",
        "drones", "uav", "manipulation", "robot perception",
    },
    # --- Blockchain / Web3 ---
    {
        "blockchain", "distributed ledger", "smart contracts",
        "web3", "cryptocurrency",
    },
    # --- Bioinformatics / Computational Biology ---
    {
        "bioinformatics", "computational biology", "genomics",
        "proteomics", "sequence analysis", "drug discovery",
    },
    # --- Healthcare / Medicine ---
    {
        "healthcare", "medicine", "clinical", "public health",
        "mental health", "oncology", "biomedical", "pharma",
        "pharmacology", "telehealth", "epidemiology",
    },
    # --- Renewable Energy / Climate ---
    {
        "climate", "climate change", "renewable energy", "sustainability",
        "carbon", "emissions", "energy storage", "solar", "wind energy",
        "green technology", "net zero", "battery",
    },
    # --- Smart Agriculture ---
    {
        "agriculture", "smart agriculture", "farming", "crop",
        "soil", "marine biology", "precision agriculture",
        "aquaculture", "livestock",
    },
    # --- Materials / Chemistry ---
    {
        "chemistry", "materials science", "nanomaterials", "polymers",
        "organic chemistry", "inorganic chemistry", "catalysis",
    },
    # --- Education / Pedagogy ---
    {
        "education", "pedagogy", "curriculum", "e-learning",
        "educational technology", "learning analytics", "stem education",
    },
    # --- Physics / Quantum ---
    {
        "quantum computing", "quantum physics", "quantum information",
        "quantum mechanics",
    },
    # --- Social Sciences / Humanities ---
    {
        "sociology", "psychology", "economics", "political science",
        "anthropology", "linguistics", "history",
    },
]


_PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
_WS_RE = re.compile(r"\s+")


def _normalize_term(term: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    if not term:
        return ""
    t = term.lower().strip()
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def _normalized_groups() -> list[set[str]]:
    """Pre-normalized view of SYNONYM_GROUPS, computed once on first use."""
    if not hasattr(_normalized_groups, "_cache"):
        _normalized_groups._cache = [
            {_normalize_term(t) for t in group if t and t.strip()}
            for group in SYNONYM_GROUPS
        ]
    return _normalized_groups._cache  # type: ignore[attr-defined]


def expand_terms(terms: Iterable[str]) -> set[str]:
    """Return the union of all synonym groups that share a term with ``terms``.

    The returned set contains the normalized (lowercase, punctuation-stripped)
    form of every related term. The input terms themselves are also included
    so that the result can be used directly as a search vocabulary.
    """
    expanded: set[str] = set()
    seeds: set[str] = set()
    for t in terms:
        n = _normalize_term(t)
        if n:
            seeds.add(n)
            expanded.add(n)
    if not seeds:
        return expanded
    for group in _normalized_groups():
        if seeds & group:
            expanded |= group
    return expanded


def contains_any(text: str, vocab: Iterable[str]) -> bool:
    """Return True if ``text`` contains any of the supplied vocabulary terms.

    The check is case-insensitive and ignores the punctuation differences that
    ``_normalize_term`` removes — so the same canonicalisation is used
    everywhere a vocabulary is compared against free text.
    """
    if not text or not vocab:
        return False
    norm_text = _normalize_term(text)
    if not norm_text:
        return False
    for term in vocab:
        nt = _normalize_term(term)
        if nt and nt in norm_text:
            return True
    return False
