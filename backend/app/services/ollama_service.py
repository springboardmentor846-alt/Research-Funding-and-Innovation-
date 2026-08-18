import json
from typing import Any, Dict, List, Optional

from ollama import Client


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

client = Client(host="http://127.0.0.1:11434")

# You already installed this model.
MODEL_NAME = "qwen2.5:1.5b"


# ============================================================
# COMMON HELPERS
# ============================================================

def _text(value: Any, default: str = "") -> str:
    """Convert any AI value safely into a string."""
    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip()
        if not value or value == "...":
            return default
        return value

    if isinstance(value, dict):
        parts = []
        for key, val in value.items():
            val_text = _text(val)
            if val_text:
                parts.append(
                    f"{str(key).replace('_', ' ').title()}: {val_text}"
                )
        return " | ".join(parts) if parts else default

    if isinstance(value, list):
        parts = [_text(item) for item in value]
        parts = [item for item in parts if item]
        return "; ".join(parts) if parts else default

    return str(value)


def _get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    value = data.get(key, default)
    return default if value is None else value


def _list_strings(value: Any, defaults: Optional[List[str]] = None) -> List[str]:
    """
    Normalize AI output to List[str].
    Handles strings, dictionaries, nested lists and None.
    """
    fallback = defaults or []

    if value is None:
        return fallback.copy()

    if isinstance(value, str):
        value = value.strip()
        if not value or value == "...":
            return fallback.copy()
        return [value]

    if isinstance(value, dict):
        converted = _text(value)
        return [converted] if converted else fallback.copy()

    if not isinstance(value, list):
        converted = _text(value)
        return [converted] if converted else fallback.copy()

    result: List[str] = []

    for item in value:
        if isinstance(item, str):
            item = item.strip()
            if item and item != "...":
                result.append(item)

        elif isinstance(item, dict):
            converted = _text(item)
            if converted:
                result.append(converted)

        else:
            converted = _text(item)
            if converted:
                result.append(converted)

    return result if result else fallback.copy()


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _object_list(
    value: Any,
    fields: List[str],
    defaults: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Normalize a list of objects to the exact fields expected by
    the Pydantic response schemas.
    """
    if not isinstance(value, list):
        return [item.copy() for item in defaults]

    result: List[Dict[str, Any]] = []

    for item in value:
        if isinstance(item, str):
            if not item.strip():
                continue

            obj = {field: "" for field in fields}
            obj[fields[0]] = item.strip()
            result.append(obj)
            continue

        if not isinstance(item, dict):
            continue

        obj = {}
        for field in fields:
            obj[field] = _text(item.get(field), "")

        # Common aliases produced by smaller models.
        aliases = {
            "startup_name": ["name", "title"],
            "product_name": ["name", "title"],
            "industry": ["name"],
            "application": ["description", "impact"],
            "model": ["name", "type"],
            "reason": ["description", "benefits", "impact"],
            "title": ["name"],
            "novelty": ["description", "impact"],
            "strategy_name": ["name", "strategy", "title"],
            "description": ["impact", "benefits", "reason"],
            "technique": ["name"],
            "challenge": ["name"],
            "methodology": ["method", "name"],
            "advantages": ["benefits", "strengths"],
            "disadvantages": ["limitations", "weaknesses"],
            "topic": ["name"],
            "keyword": ["name"],
            "trend": ["name"],
            "importance": ["impact"],
        }

        for field in fields:
            if obj[field]:
                continue

            for alias in aliases.get(field, []):
                if item.get(alias) is not None:
                    obj[field] = _text(item.get(alias), "")
                    if obj[field]:
                        break

        # Every required string field must contain something.
        for field in fields:
            if not obj[field]:
                obj[field] = "Not specified by the model."

        result.append(obj)

    return result if result else [item.copy() for item in defaults]


def _ask_json(prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Central Ollama call.

    The model can occasionally return incomplete JSON. We therefore:
    1. request JSON,
    2. parse it,
    3. merge it with the required fallback structure.
    """
    try:
        response = client.chat(
            model=MODEL_NAME,
            format="json",
            options={
                "temperature": 0.2,
                "num_ctx": 4096,
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a structured research assistant. "
                        "Return valid JSON only. Never use markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response["message"]["content"].strip()

        print("\n========== OLLAMA RESPONSE ==========")
        print(content)
        print("=====================================\n")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            print("WARNING: Ollama returned invalid JSON.")
            return fallback.copy()

        if not isinstance(parsed, dict):
            return fallback.copy()

        # Keep model output, but ensure every required top-level field exists.
        result = fallback.copy()
        result.update(parsed)
        return result

    except Exception as exc:
        print(f"OLLAMA ERROR: {exc}")
        return fallback.copy()


# ============================================================
# 1. RESEARCH SUMMARY
# ============================================================

def summarize_research(title: str, abstract: str):
    fallback = {
        "summary": f"This research examines {title}.",
        "objective": f"To study and evaluate the research problem described in {title}.",
        "methodology": "The methodology is based on the approach described in the research abstract.",
        "key_findings": "The research presents findings related to the stated research problem.",
        "future_scope": "Future work can include larger datasets, stronger validation and real-world deployment.",
        "innovation_opportunities": [
            {
                "strategy_name": "Practical Application",
                "description": f"Develop a practical solution based on {title}."
            },
            {
                "strategy_name": "Scalability",
                "description": "Improve scalability and real-world usability."
            },
            {
                "strategy_name": "Industry Adoption",
                "description": "Evaluate opportunities for adoption in relevant industries."
            },
        ],
    }

    prompt = f"""
Analyze this research paper.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON with EXACTLY these fields:

{{
  "summary": "string",
  "objective": "string",
  "methodology": "string",
  "key_findings": "string",
  "future_scope": "string",
  "innovation_opportunities": [
    {{
      "strategy_name": "string",
      "description": "string"
    }}
  ]
}}

Include all fields. Do not return null or "...".
"""

    result = _ask_json(prompt, fallback)

    opportunities = _object_list(
        result.get("innovation_opportunities"),
        ["strategy_name", "description"],
        fallback["innovation_opportunities"],
    )

    return {
        "summary": _text(result.get("summary"), fallback["summary"]),
        "objective": _text(result.get("objective"), fallback["objective"]),
        "methodology": _text(result.get("methodology"), fallback["methodology"]),
        "key_findings": _text(result.get("key_findings"), fallback["key_findings"]),
        "future_scope": _text(result.get("future_scope"), fallback["future_scope"]),
        "innovation_opportunities": opportunities,
    }


# ============================================================
# 2. INNOVATION GENERATOR
# ============================================================

def generate_innovation(title: str, abstract: str):
    fallback = {
        "problem_statement": f"The research addresses challenges related to {title}.",
        "startup_ideas": [
            {
                "startup_name": f"{title} Solutions",
                "description": "A startup that commercializes the research as a practical solution.",
                "target_customers": "Organizations and users in the relevant domain.",
                "revenue_model": "Subscription and enterprise licensing.",
            }
        ],
        "product_ideas": [
            {
                "product_name": f"{title} Platform",
                "description": "A software product based on the research concept.",
            }
        ],
        "industry_applications": [
            {
                "industry": "Technology",
                "application": f"Apply {title} to build practical technology solutions.",
            }
        ],
        "business_models": [
            {
                "model": "SaaS",
                "reason": "The solution can be delivered through a subscription platform.",
            }
        ],
        "patent_opportunities": [
            {
                "title": f"Novel {title} System",
                "novelty": "A domain-specific implementation of the research concept.",
            }
        ],
        "market_analysis": {
            "market_size": "Potential market depends on the application domain.",
            "competition": "Existing technology providers may be competitors.",
            "growth_potential": "Moderate to high if the solution is validated.",
        },
        "technology_readiness": {
            "trl": "TRL 3-5",
            "reason": "Prototype development and validation are still required.",
        },
        "commercialization_plan": {
            "first_step": "Develop and validate a proof of concept.",
            "partners": "Universities, startups and industry partners.",
            "timeline": "6-12 months for initial validation.",
        },
    }

    prompt = f"""
Act as an innovation consultant.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON matching this EXACT structure:

{{
  "problem_statement": "string",
  "startup_ideas": [
    {{
      "startup_name": "string",
      "description": "string",
      "target_customers": "string",
      "revenue_model": "string"
    }}
  ],
  "product_ideas": [
    {{
      "product_name": "string",
      "description": "string"
    }}
  ],
  "industry_applications": [
    {{
      "industry": "string",
      "application": "string"
    }}
  ],
  "business_models": [
    {{
      "model": "string",
      "reason": "string"
    }}
  ],
  "patent_opportunities": [
    {{
      "title": "string",
      "novelty": "string"
    }}
  ],
  "market_analysis": {{
    "market_size": "string",
    "competition": "string",
    "growth_potential": "string"
  }},
  "technology_readiness": {{
    "trl": "string",
    "reason": "string"
  }},
  "commercialization_plan": {{
    "first_step": "string",
    "partners": "string",
    "timeline": "string"
  }}
}}

Every field is REQUIRED.
"""

    result = _ask_json(prompt, fallback)

    startup_ideas = _object_list(
        result.get("startup_ideas"),
        ["startup_name", "description", "target_customers", "revenue_model"],
        fallback["startup_ideas"],
    )

    product_ideas = _object_list(
        result.get("product_ideas"),
        ["product_name", "description"],
        fallback["product_ideas"],
    )

    industry_applications = _object_list(
        result.get("industry_applications"),
        ["industry", "application"],
        fallback["industry_applications"],
    )

    business_models = _object_list(
        result.get("business_models"),
        ["model", "reason"],
        fallback["business_models"],
    )

    patent_opportunities = _object_list(
        result.get("patent_opportunities"),
        ["title", "novelty"],
        fallback["patent_opportunities"],
    )

    market = _dict(result.get("market_analysis"))
    technology = _dict(result.get("technology_readiness"))
    commercialization = _dict(result.get("commercialization_plan"))

    return {
        "problem_statement": _text(
            result.get("problem_statement"),
            fallback["problem_statement"],
        ),
        "startup_ideas": startup_ideas,
        "product_ideas": product_ideas,
        "industry_applications": industry_applications,
        "business_models": business_models,
        "patent_opportunities": patent_opportunities,
        "market_analysis": {
            "market_size": _text(
                market.get("market_size"),
                fallback["market_analysis"]["market_size"],
            ),
            "competition": _text(
                market.get("competition"),
                fallback["market_analysis"]["competition"],
            ),
            "growth_potential": _text(
                market.get("growth_potential"),
                fallback["market_analysis"]["growth_potential"],
            ),
        },
        "technology_readiness": {
            "trl": _text(
                technology.get("trl"),
                fallback["technology_readiness"]["trl"],
            ),
            "reason": _text(
                technology.get("reason"),
                fallback["technology_readiness"]["reason"],
            ),
        },
        "commercialization_plan": {
            "first_step": _text(
                commercialization.get("first_step"),
                fallback["commercialization_plan"]["first_step"],
            ),
            "partners": _text(
                commercialization.get("partners"),
                fallback["commercialization_plan"]["partners"],
            ),
            "timeline": _text(
                commercialization.get("timeline"),
                fallback["commercialization_plan"]["timeline"],
            ),
        },
    }


# ============================================================
# 3. RESEARCH GAP
# ============================================================

def detect_research_gap(title: str, abstract: str):
    fallback = {
        "limitations": [
            "The available abstract provides limited experimental detail.",
            "The scope may require validation on larger datasets.",
        ],
        "research_gaps": [
            "Additional empirical validation is required.",
            "Real-world deployment scenarios need further study.",
        ],
        "future_directions": [
            "Evaluate the approach on larger and more diverse datasets.",
            "Test the approach in real-world environments.",
        ],
        "novel_opportunities": [
            "Develop practical applications based on the identified gap.",
            "Combine the approach with complementary technologies.",
        ],
        "interdisciplinary_opportunities": [
            "Combine computer science with the relevant application domain.",
            "Collaborate with domain experts for practical validation.",
        ],
    }

    prompt = f"""
Analyze research gaps in:

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "limitations": ["string", "string"],
  "research_gaps": ["string", "string"],
  "future_directions": ["string", "string"],
  "novel_opportunities": ["string", "string"],
  "interdisciplinary_opportunities": ["string", "string"]
}}

All array elements MUST be strings.
"""

    result = _ask_json(prompt, fallback)

    return {
        "limitations": _list_strings(result.get("limitations"), fallback["limitations"]),
        "research_gaps": _list_strings(result.get("research_gaps"), fallback["research_gaps"]),
        "future_directions": _list_strings(
            result.get("future_directions"), fallback["future_directions"]
        ),
        "novel_opportunities": _list_strings(
            result.get("novel_opportunities"), fallback["novel_opportunities"]
        ),
        "interdisciplinary_opportunities": _list_strings(
            result.get("interdisciplinary_opportunities"),
            fallback["interdisciplinary_opportunities"],
        ),
    }


# ============================================================
# 4. LITERATURE REVIEW
# ============================================================

def generate_literature_review(title: str, abstract: str):
    fallback = {
        "overview": f"This review examines existing research related to {title}.",
        "existing_research": [
            {
                "title": "Related Research",
                "year": 2024,
                "abstract": "Related studies have investigated similar research problems.",
            }
        ],
        "key_techniques": [
            {
                "technique": "Machine Learning",
                "description": "Machine learning can be used to analyze research data.",
            }
        ],
        "research_challenges": [
            {
                "challenge": "Scalability",
                "description": "Scaling research solutions to real-world environments can be challenging.",
            }
        ],
        "comparison": [
            {
                "methodology": "Existing approach",
                "advantages": "Provides an established baseline.",
                "disadvantages": "May require further optimization.",
            }
        ],
        "conclusion": "Further research and experimental validation are recommended.",
    }

    prompt = f"""
Generate a structured literature review.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "overview": "string",
  "existing_research": [
    {{
      "title": "string",
      "year": 2024,
      "abstract": "string"
    }}
  ],
  "key_techniques": [
    {{
      "technique": "string",
      "description": "string"
    }}
  ],
  "research_challenges": [
    {{
      "challenge": "string",
      "description": "string"
    }}
  ],
  "comparison": [
    {{
      "methodology": "string",
      "advantages": "string",
      "disadvantages": "string"
    }}
  ],
  "conclusion": "string"
}}

Do not invent citation details. If exact papers are unavailable, describe the research generally.
"""

    result = _ask_json(prompt, fallback)

    existing = result.get("existing_research")
    if not isinstance(existing, list) or not existing:
        existing = fallback["existing_research"]

    normalized_existing = []
    for item in existing:
        if isinstance(item, dict):
            year = item.get("year")
            try:
                year = int(year) if year is not None else 2024
            except (TypeError, ValueError):
                year = 2024

            normalized_existing.append({
                "title": _text(item.get("title"), "Related Research"),
                "year": year,
                "abstract": _text(
                    item.get("abstract"),
                    "Related research has investigated similar problems.",
                ),
            })

    if not normalized_existing:
        normalized_existing = fallback["existing_research"]

    return {
        "overview": _text(result.get("overview"), fallback["overview"]),
        "existing_research": normalized_existing,
        "key_techniques": _object_list(
            result.get("key_techniques"),
            ["technique", "description"],
            fallback["key_techniques"],
        ),
        "research_challenges": _object_list(
            result.get("research_challenges"),
            ["challenge", "description"],
            fallback["research_challenges"],
        ),
        "comparison": _object_list(
            result.get("comparison"),
            ["methodology", "advantages", "disadvantages"],
            fallback["comparison"],
        ),
        "conclusion": _text(result.get("conclusion"), fallback["conclusion"]),
    }


# ============================================================
# 5. RESEARCH TRENDS
# ============================================================

def analyze_research_trends(title: str, abstract: str):
    fallback = {
        "trending_topics": [
            {
                "topic": title,
                "reason": "The topic is relevant to current research activity.",
            }
        ],
        "emerging_keywords": [
            {
                "keyword": "Artificial Intelligence",
                "importance": "High",
            }
        ],
        "future_trends": [
            {
                "trend": "Real-world deployment",
                "impact": "High",
            }
        ],
        "publication_growth": "Research activity is expected to continue growing.",
        "recommendation": "Focus on practical validation and emerging technologies.",
    }

    prompt = f"""
Analyze research trends.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "trending_topics": [
    {{
      "topic": "string",
      "reason": "string"
    }}
  ],
  "emerging_keywords": [
    {{
      "keyword": "string",
      "importance": "string"
    }}
  ],
  "future_trends": [
    {{
      "trend": "string",
      "impact": "string"
    }}
  ],
  "publication_growth": "string",
  "recommendation": "string"
}}
"""

    result = _ask_json(prompt, fallback)

    return {
        "trending_topics": _object_list(
            result.get("trending_topics"),
            ["topic", "reason"],
            fallback["trending_topics"],
        ),
        "emerging_keywords": _object_list(
            result.get("emerging_keywords"),
            ["keyword", "importance"],
            fallback["emerging_keywords"],
        ),
        "future_trends": _object_list(
            result.get("future_trends"),
            ["trend", "impact"],
            fallback["future_trends"],
        ),
        "publication_growth": _text(
            result.get("publication_growth"),
            fallback["publication_growth"],
        ),
        "recommendation": _text(
            result.get("recommendation"),
            fallback["recommendation"],
        ),
    }


# ============================================================
# 6. CITATION INTELLIGENCE
# ============================================================

def generate_citations(
    title: str,
    authors: List[str],
    journal: Optional[str] = None,
    publication_year: Optional[int] = None,
    doi: Optional[str] = None,
):
    author_text = ", ".join(authors or ["Unknown Author"])
    year = publication_year or "n.d."
    journal_text = journal or "Unknown Journal"

    fallback = {
        "apa": f"{author_text}. ({year}). {title}. {journal_text}.",
        "ieee": f"{author_text}, \"{title},\" {journal_text}, {year}.",
        "mla": f"{author_text}. \"{title}.\" {journal_text}, {year}.",
        "chicago": f"{author_text}. \"{title}.\" {journal_text}, {year}.",
        "bibtex": (
            "@article{research,\n"
            f"  title={{ {title} }},\n"
            f"  author={{ {author_text} }},\n"
            f"  journal={{ {journal_text} }},\n"
            f"  year={{ {publication_year or ''} }},\n"
            f"  doi={{ {doi or ''} }}\n"
            "}"
        ),
        "ris": (
            "TY  - JOUR\n"
            f"TI  - {title}\n"
            f"AU  - {author_text}\n"
            f"JO  - {journal_text}\n"
            f"PY  - {publication_year or ''}\n"
            f"DO  - {doi or ''}\n"
            "ER  -"
        ),
    }

    prompt = f"""
Generate citations for this research paper.

Title: {title}
Authors: {author_text}
Journal: {journal_text}
Year: {publication_year}
DOI: {doi}

Return ONLY JSON:

{{
  "apa": "string",
  "ieee": "string",
  "mla": "string",
  "chicago": "string",
  "bibtex": "string",
  "ris": "string"
}}
"""

    result = _ask_json(prompt, fallback)

    return {
        key: _text(result.get(key), fallback[key])
        for key in fallback
    }


# ============================================================
# 7. RESEARCH CHAT
# ============================================================

def research_chat(title: str, abstract: str, question: str):
    fallback = {
        "answer": (
            f"Based on the provided abstract for '{title}', "
            f"the research is concerned with the stated topic. "
            f"The abstract says: {abstract}"
        )
    }

    prompt = f"""
You are a research assistant.

Paper title:
{title}

Abstract:
{abstract}

Question:
{question}

Answer using only the information provided.

Return ONLY JSON:
{{
  "answer": "clear answer"
}}
"""

    result = _ask_json(prompt, fallback)

    return {
        "answer": _text(result.get("answer"), fallback["answer"])
    }


# ============================================================
# 8. PAPER COMPARATOR
# ============================================================

def compare_research_papers(
    title1: str,
    abstract1: str,
    title2: str,
    abstract2: str,
):
    fallback = {
        "similarities": [
            "Both papers address research problems within their respective topics."
        ],
        "differences": [
            "The papers may differ in objectives, methodology and application."
        ],
        "strengths_paper1": [
            "Provides a focused research perspective."
        ],
        "strengths_paper2": [
            "Provides an alternative research perspective."
        ],
        "weaknesses_paper1": [
            "Detailed evaluation requires complete paper information."
        ],
        "weaknesses_paper2": [
            "Detailed evaluation requires complete paper information."
        ],
        "recommendation": "Compare methodology, datasets and experimental results before selecting an approach.",
    }

    prompt = f"""
Compare two research papers.

PAPER 1
Title: {title1}
Abstract: {abstract1}

PAPER 2
Title: {title2}
Abstract: {abstract2}

Return ONLY JSON:

{{
  "similarities": ["string", "string"],
  "differences": ["string", "string"],
  "strengths_paper1": ["string", "string"],
  "strengths_paper2": ["string", "string"],
  "weaknesses_paper1": ["string", "string"],
  "weaknesses_paper2": ["string", "string"],
  "recommendation": "string"
}}

All array values MUST be strings.
"""

    result = _ask_json(prompt, fallback)

    return {
        "similarities": _list_strings(
            result.get("similarities"), fallback["similarities"]
        ),
        "differences": _list_strings(
            result.get("differences"), fallback["differences"]
        ),
        "strengths_paper1": _list_strings(
            result.get("strengths_paper1"), fallback["strengths_paper1"]
        ),
        "strengths_paper2": _list_strings(
            result.get("strengths_paper2"), fallback["strengths_paper2"]
        ),
        "weaknesses_paper1": _list_strings(
            result.get("weaknesses_paper1"), fallback["weaknesses_paper1"]
        ),
        "weaknesses_paper2": _list_strings(
            result.get("weaknesses_paper2"), fallback["weaknesses_paper2"]
        ),
        "recommendation": _text(
            result.get("recommendation"), fallback["recommendation"]
        ),
    }


# ============================================================
# 9. RESEARCH PROPOSAL
# ============================================================

def generate_research_proposal(title: str, abstract: str):
    fallback = {
        "problem_statement": f"The proposal investigates the research problem described by {title}.",
        "objectives": [
            "Analyze the research problem.",
            "Develop an appropriate solution.",
            "Evaluate the proposed approach.",
        ],
        "literature_review": "Existing research provides the foundation for the proposed study.",
        "methodology": "Define the problem, collect data, implement the approach and evaluate results.",
        "expected_outcomes": [
            "A validated solution.",
            "Experimental results.",
            "Improved understanding of the research problem.",
        ],
        "future_scope": "The work can be extended using larger datasets and real-world deployment.",
        "timeline": "Literature review -> implementation -> testing -> evaluation.",
    }

    prompt = f"""
Generate a research proposal.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "problem_statement": "string",
  "objectives": ["string", "string", "string"],
  "literature_review": "string",
  "methodology": "string",
  "expected_outcomes": ["string", "string", "string"],
  "future_scope": "string",
  "timeline": "string"
}}
"""

    result = _ask_json(prompt, fallback)

    return {
        "problem_statement": _text(
            result.get("problem_statement"),
            fallback["problem_statement"],
        ),
        "objectives": _list_strings(
            result.get("objectives"),
            fallback["objectives"],
        ),
        "literature_review": _text(
            result.get("literature_review"),
            fallback["literature_review"],
        ),
        "methodology": _text(
            result.get("methodology"),
            fallback["methodology"],
        ),
        "expected_outcomes": _list_strings(
            result.get("expected_outcomes"),
            fallback["expected_outcomes"],
        ),
        "future_scope": _text(
            result.get("future_scope"),
            fallback["future_scope"],
        ),
        "timeline": _text(
            result.get("timeline"),
            fallback["timeline"],
        ),
    }


# ============================================================
# 10. NOVELTY CHECKER
# ============================================================

def check_novelty(title: str, abstract: str):
    fallback = {
        "novelty_score": 70,
        "innovation_level": "Moderate",
        "uniqueness": "The idea may contain useful innovation depending on its implementation.",
        "similar_research": [
            "Related research may already exist."
        ],
        "unique_contributions": [
            "Potential domain-specific implementation.",
            "Potential practical improvement.",
        ],
        "patent_potential": "Patent potential requires a detailed prior-art search.",
        "improvement_suggestions": [
            "Clearly define the novel technical contribution.",
            "Compare against existing solutions.",
            "Validate the innovation experimentally.",
        ],
    }

    prompt = f"""
Analyze the novelty of this research.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "novelty_score": 70,
  "innovation_level": "string",
  "uniqueness": "string",
  "similar_research": ["string", "string"],
  "unique_contributions": ["string", "string"],
  "patent_potential": "string",
  "improvement_suggestions": ["string", "string"]
}}

novelty_score must be an integer from 0 to 100.
"""

    result = _ask_json(prompt, fallback)

    try:
        score = int(result.get("novelty_score", fallback["novelty_score"]))
        score = max(0, min(100, score))
    except (TypeError, ValueError):
        score = fallback["novelty_score"]

    return {
        "novelty_score": score,
        "innovation_level": _text(
            result.get("innovation_level"),
            fallback["innovation_level"],
        ),
        "uniqueness": _text(
            result.get("uniqueness"),
            fallback["uniqueness"],
        ),
        "similar_research": _list_strings(
            result.get("similar_research"),
            fallback["similar_research"],
        ),
        "unique_contributions": _list_strings(
            result.get("unique_contributions"),
            fallback["unique_contributions"],
        ),
        "patent_potential": _text(
            result.get("patent_potential"),
            fallback["patent_potential"],
        ),
        "improvement_suggestions": _list_strings(
            result.get("improvement_suggestions"),
            fallback["improvement_suggestions"],
        ),
    }


# ============================================================
# 11. RESEARCH QUESTION GENERATOR
# ============================================================

def generate_research_questions(title: str, abstract: str):
    fallback = {
        "research_questions": [
            f"What are the main challenges associated with {title}?",
            "How can the proposed approach be improved?",
            "How effective is the approach in real-world conditions?",
        ],
        "objectives": [
            "Analyze the research problem.",
            "Develop an appropriate solution.",
            "Evaluate the proposed approach.",
        ],
        "hypotheses": [
            "The proposed approach can improve the target problem.",
            "The approach can achieve measurable improvements.",
        ],
        "research_scope": f"The study focuses on {title} and its practical applications.",
        "future_research_directions": [
            "Use larger datasets.",
            "Evaluate additional environments.",
            "Explore advanced techniques.",
        ],
    }

    prompt = f"""
Generate research questions for:

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "research_questions": ["string", "string", "string"],
  "objectives": ["string", "string", "string"],
  "hypotheses": ["string", "string"],
  "research_scope": "string",
  "future_research_directions": ["string", "string", "string"]
}}

All arrays must contain strings.
"""

    result = _ask_json(prompt, fallback)

    return {
        "research_questions": _list_strings(
            result.get("research_questions"),
            fallback["research_questions"],
        ),
        "objectives": _list_strings(
            result.get("objectives"),
            fallback["objectives"],
        ),
        "hypotheses": _list_strings(
            result.get("hypotheses"),
            fallback["hypotheses"],
        ),
        "research_scope": _text(
            result.get("research_scope"),
            fallback["research_scope"],
        ),
        "future_research_directions": _list_strings(
            result.get("future_research_directions"),
            fallback["future_research_directions"],
        ),
    }


# ============================================================
# 12. METHODOLOGY RECOMMENDER
# ============================================================

def recommend_methodology(title: str, abstract: str):
    fallback = {
        "recommended_methodology": "Experimental research methodology",
        "algorithms": [
            "Machine Learning",
            "Deep Learning",
            "Statistical Analysis",
        ],
        "datasets": [
            "Public benchmark datasets",
            "Domain-specific datasets",
            "Real-world collected datasets",
        ],
        "tools_frameworks": [
            "Python",
            "Scikit-learn",
            "Jupyter Notebook",
        ],
        "evaluation_metrics": [
            "Accuracy",
            "Precision",
            "Recall",
        ],
        "experimental_setup": (
            "Prepare the dataset, preprocess data, train the selected "
            "models and evaluate their performance."
        ),
        "validation_techniques": [
            "Train-test split",
            "Cross-validation",
            "Performance comparison",
        ],
    }

    prompt = f"""
Recommend a research methodology.

TITLE:
{title}

ABSTRACT:
{abstract}

Return ONLY JSON:

{{
  "recommended_methodology": "string",
  "algorithms": ["string", "string", "string"],
  "datasets": ["string", "string", "string"],
  "tools_frameworks": ["string", "string", "string"],
  "evaluation_metrics": ["string", "string", "string"],
  "experimental_setup": "string",
  "validation_techniques": ["string", "string", "string"]
}}

All array values MUST be strings.
"""

    result = _ask_json(prompt, fallback)

    return {
        "recommended_methodology": _text(
            result.get("recommended_methodology"),
            fallback["recommended_methodology"],
        ),
        "algorithms": _list_strings(
            result.get("algorithms"),
            fallback["algorithms"],
        ),
        "datasets": _list_strings(
            result.get("datasets"),
            fallback["datasets"],
        ),
        "tools_frameworks": _list_strings(
            result.get("tools_frameworks"),
            fallback["tools_frameworks"],
        ),
        "evaluation_metrics": _list_strings(
            result.get("evaluation_metrics"),
            fallback["evaluation_metrics"],
        ),
        "experimental_setup": _text(
            result.get("experimental_setup"),
            fallback["experimental_setup"],
        ),
        "validation_techniques": _list_strings(
            result.get("validation_techniques"),
            fallback["validation_techniques"],
        ),
    }