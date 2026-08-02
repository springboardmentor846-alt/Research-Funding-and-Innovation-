import json
from ollama import Client

client = Client(host="http://127.0.0.1:11434")


# =====================================================
# AI Research Summarizer
# =====================================================

def summarize_research(title: str, abstract: str):
    """
    Generate a structured AI summary for a research paper.
    """

    prompt = f"""
You are an expert research analyst.

Analyze the following paper.

Title:
{title}

Abstract:
{abstract}

Return ONLY valid JSON in this exact format:

{{
    "summary": "...",
    "objective": "...",
    "methodology": "...",
    "key_findings": "...",
    "future_scope": "...",
    "innovation_opportunities": [
        "...",
        "...",
        "..."
    ]
}}

Return ONLY JSON.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RAW OLLAMA RESPONSE ==========")
    print(content)
    print("=========================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError as e:
        print("JSON ERROR:", e)

        return {
            "summary": content,
            "objective": "",
            "methodology": "",
            "key_findings": "",
            "future_scope": "",
            "innovation_opportunities": []
        }

    return {
        "summary": result.get("summary", ""),
        "objective": result.get("objective", ""),
        "methodology": result.get("methodology", ""),
        "key_findings": result.get("key_findings", ""),
        "future_scope": result.get("future_scope", ""),
        "innovation_opportunities": result.get(
            "innovation_opportunities", []
        )
    }


# =====================================================
# AI Innovation Generator
# =====================================================

def generate_innovation(title: str, abstract: str):
    """
    Generate innovation insights from a research paper.
    """

    prompt = f"""
You are an Innovation Consultant, Startup Mentor, Patent Expert, and Business Strategist.

Analyze the following research paper.

Title:
{title}

Abstract:
{abstract}

Return ONLY valid JSON in the following format.

{{
    "problem_statement": "...",

    "startup_ideas": [
        {{
            "startup_name": "...",
            "description": "...",
            "target_customers": "...",
            "revenue_model": "..."
        }}
    ],

    "product_ideas": [
        {{
            "product_name": "...",
            "description": "..."
        }}
    ],

    "industry_applications": [
        {{
            "industry": "...",
            "application": "..."
        }}
    ],

    "business_models": [
        {{
            "model": "...",
            "reason": "..."
        }}
    ],

    "patent_opportunities": [
        {{
            "title": "...",
            "novelty": "..."
        }}
    ],

    "market_analysis": {{
        "market_size": "...",
        "competition": "...",
        "growth_potential": "..."
    }},

    "technology_readiness": {{
        "trl": "...",
        "reason": "..."
    }},

    "commercialization_plan": {{
        "first_step": "...",
        "partners": "...",
        "timeline": "..."
    }}
}}

Rules:
- Return ONLY JSON.
- Never return markdown.
- Never return explanations.
- Never leave fields empty.
- Infer reasonable values if information is limited.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RAW INNOVATION RESPONSE ==========")
    print(content)
    print("=============================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError as e:
        print("JSON ERROR:", e)

        return {
            "problem_statement": "",

            "startup_ideas": [],

            "product_ideas": [],

            "industry_applications": [],

            "business_models": [],

            "patent_opportunities": [],

            "market_analysis": {
                "market_size": "",
                "competition": "",
                "growth_potential": ""
            },

            "technology_readiness": {
                "trl": "",
                "reason": ""
            },

            "commercialization_plan": {
                "first_step": "",
                "partners": "",
                "timeline": ""
            }
        }

    return result
def detect_research_gap(title: str, abstract: str):
    """
    Detect research gaps, limitations, and future opportunities.
    """

    prompt = f"""
You are an expert Research Scientist.

Analyze the following research paper.

Title:
{title}

Abstract:
{abstract}

Return ONLY valid JSON in the following format.

{{
    "limitations": [
        "..."
    ],

    "research_gaps": [
        "..."
    ],

    "future_directions": [
        "..."
    ],

    "novel_opportunities": [
        "..."
    ],

    "interdisciplinary_opportunities": [
        "..."
    ]
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanations.
- If information is limited, infer reasonable research gaps.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RESEARCH GAP RESPONSE ==========")
    print(content)
    print("===========================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "limitations": [],
            "research_gaps": [],
            "future_directions": [],
            "novel_opportunities": [],
            "interdisciplinary_opportunities": []
        }

    return result
def generate_literature_review(title: str, abstract: str):
    """
    Generate a structured literature review using Ollama.
    """

    prompt = f"""
You are an expert Research Scientist and Literature Review Specialist.

Analyze the following research paper.

Title:
{title}

Abstract:
{abstract}

Generate a structured literature review.

Return ONLY valid JSON in the following format.

{{
    "overview": "...",

    "existing_research": [
        {{
            "title": "...",
            "year": 2024,
            "abstract": "..."
        }}
    ],

    "key_techniques": [
        {{
            "technique": "...",
            "description": "..."
        }}
    ],

    "research_challenges": [
        {{
            "challenge": "...",
            "description": "..."
        }}
    ],

    "comparison": [
        {{
            "methodology": "...",
            "advantages": "...",
            "disadvantages": "..."
        }}
    ],

    "conclusion": "..."
}}

IMPORTANT RULES:
- Return ONLY valid JSON.
- Do NOT return markdown.
- Do NOT add explanations.
- Use EXACTLY the field names shown above.
- Do NOT use 'title' instead of 'technique'.
- Do NOT use 'summary' instead of 'abstract'.
- Do NOT use 'method' instead of 'methodology'.
- Every object must contain all required fields.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== LITERATURE REVIEW RESPONSE ==========")
    print(content)
    print("================================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "overview": "",
            "existing_research": [],
            "key_techniques": [],
            "research_challenges": [],
            "comparison": [],
            "conclusion": ""
        }

    return result
def analyze_research_trends(title: str, abstract: str):
    """
    Analyze research trends using Ollama.
    """

    prompt = f"""
You are an expert Research Trend Analyst.

Analyze the following research paper.

Title:
{title}

Abstract:
{abstract}

Identify current and future research trends.

Return ONLY valid JSON in the following format.

{{
    "trending_topics": [
        {{
            "topic": "...",
            "reason": "..."
        }}
    ],

    "emerging_keywords": [
        {{
            "keyword": "...",
            "importance": "..."
        }}
    ],

    "future_trends": [
        {{
            "trend": "...",
            "impact": "..."
        }}
    ],

    "publication_growth": "...",

    "recommendation": "..."
}}

Rules:
- Return ONLY valid JSON.
- Do NOT return markdown.
- Do NOT return explanations.
- Use EXACTLY the field names shown above.
- Every object must contain all required fields.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RESEARCH TREND RESPONSE ==========")
    print(content)
    print("=============================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "trending_topics": [],
            "emerging_keywords": [],
            "future_trends": [],
            "publication_growth": "",
            "recommendation": ""
        }

    return result
# =====================================================
# Citation Intelligence
# =====================================================

def generate_citations(
    title: str,
    authors: list,
    journal: str = "",
    publication_year: int = None,
    doi: str = ""
):
    """
    Generate citations in multiple formats.
    """

    prompt = f"""
You are an expert academic citation generator.

Generate citations for the following research paper.

Title:
{title}

Authors:
{", ".join(authors)}

Journal:
{journal}

Publication Year:
{publication_year}

DOI:
{doi}

Return ONLY valid JSON.

{{
    "apa": "...",
    "ieee": "...",
    "mla": "...",
    "chicago": "...",
    "bibtex": "...",
    "ris": "..."
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanations.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== CITATION RESPONSE ==========")
    print(content)
    print("=======================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "apa": "",
            "ieee": "",
            "mla": "",
            "chicago": "",
            "bibtex": "",
            "ris": ""
        }

    return {
        "apa": result.get("apa", ""),
        "ieee": result.get("ieee", ""),
        "mla": result.get("mla", ""),
        "chicago": result.get("chicago", ""),
        "bibtex": result.get("bibtex", ""),
        "ris": result.get("ris", "")
    }


# =====================================================
# AI Research Chat Assistant
# =====================================================

def research_chat(title: str, abstract: str, question: str):
    """
    AI Chat Assistant for Research Papers.
    """

    prompt = f"""
You are an expert Research Assistant.

Research Paper Title:
{title}

Abstract:
{abstract}

User Question:
{question}

Instructions:
- Answer ONLY based on the given paper.
- If the answer is not explicitly stated, infer it reasonably from the title and abstract.
- Keep the answer clear and concise.
- Return ONLY valid JSON.

{{
    "answer": "..."
}}
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RESEARCH CHAT RESPONSE ==========")
    print(content)
    print("============================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "answer": content
        }

    return {
        "answer": result.get(
            "answer",
            "Unable to answer the question."
        )
    }
# =====================================================
# Research Paper Comparator
# =====================================================

def compare_research_papers(
    title1: str,
    abstract1: str,
    title2: str,
    abstract2: str
):
    """
    Compare two research papers.
    """

    prompt = f"""
You are an expert Research Paper Reviewer.

Compare the following two research papers.

Paper 1

Title:
{title1}

Abstract:
{abstract1}

------------------------------------

Paper 2

Title:
{title2}

Abstract:
{abstract2}

Return ONLY valid JSON.

{{
    "similarities":[
        "...",
        "..."
    ],

    "differences":[
        "...",
        "..."
    ],

    "strengths_paper1":[
        "...",
        "..."
    ],

    "strengths_paper2":[
        "...",
        "..."
    ],

    "weaknesses_paper1":[
        "...",
        "..."
    ],

    "weaknesses_paper2":[
        "...",
        "..."
    ],

    "recommendation":"..."
}}

Rules:
- Return ONLY JSON.
- Never return markdown.
- Never leave fields empty.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== PAPER COMPARATOR RESPONSE ==========")
    print(content)
    print("===============================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "similarities": [],
            "differences": [],
            "strengths_paper1": [],
            "strengths_paper2": [],
            "weaknesses_paper1": [],
            "weaknesses_paper2": [],
            "recommendation": ""
        }

    return result
# =====================================================
# Research Proposal Generator
# =====================================================

def generate_research_proposal(title: str, abstract: str):
    """
    Generate a complete research proposal.
    """

    prompt = f"""
You are an expert Research Proposal Writer.

Based on the following research idea, generate a complete research proposal.

Title:
{title}

Abstract:
{abstract}

Return ONLY valid JSON.

{{
    "problem_statement":"...",

    "objectives":[
        "...",
        "...",
        "..."
    ],

    "literature_review":"...",

    "methodology":"...",

    "expected_outcomes":[
        "...",
        "...",
        "..."
    ],

    "future_scope":"...",

    "timeline":"..."
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanations.
- Never leave any field empty.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RESEARCH PROPOSAL RESPONSE ==========")
    print(content)
    print("================================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "problem_statement": "",
            "objectives": [],
            "literature_review": "",
            "methodology": "",
            "expected_outcomes": [],
            "future_scope": "",
            "timeline": ""
        }

    return {
    "problem_statement": result.get("problem_statement", ""),
    "objectives": result.get("objectives", []),
    "literature_review": result.get("literature_review", ""),
    "methodology": result.get("methodology", ""),
    "expected_outcomes": result.get("expected_outcomes", []),
    "future_scope": result.get("future_scope", ""),
    "timeline": result.get("timeline", "")
}

# =====================================================
# Novelty Checker
# =====================================================

def check_novelty(title: str, abstract: str):
    """
    Analyze the novelty of a research idea.
    """

    prompt = f"""
You are an expert Research Reviewer and Patent Analyst.

Analyze the novelty of the following research.

Title:
{title}

Abstract:
{abstract}

Return ONLY valid JSON.

{{
    "novelty_score": 85,
    "innovation_level": "...",
    "uniqueness": "...",

    "similar_research": [
        "...",
        "...",
        "..."
    ],

    "unique_contributions": [
        "...",
        "...",
        "..."
    ],

    "patent_potential": "...",

    "improvement_suggestions": [
        "...",
        "...",
        "..."
    ]
}}

Rules:
- novelty_score must be between 0 and 100.
- Return ONLY JSON.
- No markdown.
- Never leave any field empty.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== NOVELTY CHECKER RESPONSE ==========")
    print(content)
    print("==============================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "novelty_score": 0,
            "innovation_level": "",
            "uniqueness": "",
            "similar_research": [],
            "unique_contributions": [],
            "patent_potential": "",
            "improvement_suggestions": []
        }

    return result
# =====================================================
# Research Question Generator
# =====================================================

def generate_research_questions(title: str, abstract: str):
    """
    Generate research questions, objectives, hypotheses,
    research scope, and future research directions.
    """

    prompt = f"""
You are an expert Research Advisor.

Analyze the following research.

Title:
{title}

Abstract:
{abstract}

Generate research questions, objectives, hypotheses,
research scope, and future research directions.

Return ONLY valid JSON.

{{
    "research_questions": [
        "...",
        "...",
        "..."
    ],

    "objectives": [
        "...",
        "...",
        "..."
    ],

    "hypotheses": [
        "...",
        "...",
        "..."
    ],

    "research_scope": "...",

    "future_research_directions": [
        "...",
        "...",
        "..."
    ]
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanations.
- Never leave any field empty.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== RESEARCH QUESTION RESPONSE ==========")
    print(content)
    print("================================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        return {
            "research_questions": [],
            "objectives": [],
            "hypotheses": [],
            "research_scope": "",
            "future_research_directions": []
        }

    return {
    "research_questions": result.get("research_questions", []),
    "objectives": result.get("objectives", []),
    "hypotheses": result.get("hypotheses", []),
    "research_scope": result.get("research_scope", ""),
    "future_research_directions": result.get(
        "future_research_directions",
        [
            "Explore advanced AI models.",
            "Validate on larger datasets.",
            "Investigate real-world deployment."
        ]
    )
}
# =====================================================
# Methodology Recommender
# =====================================================

def recommend_methodology(title: str, abstract: str):
    """
    Recommend research methodology.
    """

    prompt = f"""
You are an expert Research Methodology Advisor.

Analyze the following research.

Title:
{title}

Abstract:
{abstract}

Recommend the most suitable research methodology.

Return ONLY valid JSON in the following format:

{{
    "recommended_methodology": "...",

    "algorithms": [
        "...",
        "...",
        "..."
    ],

    "datasets": [
        "...",
        "...",
        "..."
    ],

    "tools_frameworks": [
        "...",
        "...",
        "..."
    ],

    "evaluation_metrics": [
        "...",
        "...",
        "..."
    ],

    "experimental_setup": "...",

    "validation_techniques": [
        "...",
        "...",
        "..."
    ]
}}

Rules:
1. Return ONLY valid JSON.
2. Never omit any field.
3. recommended_methodology must not be empty.
4. algorithms must contain at least 3 items.
5. datasets must contain at least 3 items.
6. tools_frameworks must contain at least 3 items.
7. evaluation_metrics must contain at least 3 items.
8. validation_techniques must contain at least 3 items.
9. No markdown.
10. No explanations.
"""

    response = client.chat(
        model="llama3:latest",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    print("\n========== METHODOLOGY RESPONSE ==========")
    print(content)
    print("==========================================\n")

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        return {
            "recommended_methodology": "",
            "algorithms": [],
            "datasets": [],
            "tools_frameworks": [],
            "evaluation_metrics": [],
            "experimental_setup": "",
            "validation_techniques": []
        }

    return {
        "recommended_methodology": result.get(
            "recommended_methodology", ""
        ),

        "algorithms": result.get(
            "algorithms", []
        ),

        "datasets": result.get(
            "datasets", []
        ),

        "tools_frameworks": result.get(
            "tools_frameworks", []
        ),

        "evaluation_metrics": result.get(
            "evaluation_metrics", []
        ),

        "experimental_setup": result.get(
            "experimental_setup", ""
        ),

        "validation_techniques": result.get(
            "validation_techniques", []
        )
    }