from typing import List, Optional, Union

from pydantic import BaseModel


# ============================================================
# AUTHOR
# ============================================================

class AuthorResponse(BaseModel):
    name: str


# ============================================================
# INSTITUTION
# ============================================================

class InstitutionResponse(BaseModel):
    name: str


# ============================================================
# RESEARCH PAPER
# ============================================================

class PaperResponse(BaseModel):
    id: str
    title: str
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    cited_by_count: int
    authors: List[AuthorResponse]


# ============================================================
# PAPER SEARCH
# ============================================================

class PaperSearchResponse(BaseModel):
    count: int
    results: List[PaperResponse]


# ============================================================
# PAPER DETAIL
# ============================================================

class PaperDetailResponse(BaseModel):
    id: str
    title: str
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    cited_by_count: int
    abstract: Optional[str] = None
    journal: Optional[str] = None
    pdf_url: Optional[str] = None
    authors: List[AuthorResponse]
    institutions: List[InstitutionResponse]


# ============================================================
# AUTHOR SEARCH
# ============================================================

class AuthorSearchItem(BaseModel):
    id: str
    name: str
    orcid: Optional[str] = None
    works_count: int
    cited_by_count: int
    h_index: Optional[int] = None
    last_known_institution: Optional[str] = None


class AuthorSearchResponse(BaseModel):
    count: int
    results: List[AuthorSearchItem]


# ============================================================
# RESEARCH TOPIC
# ============================================================

class ResearchTopicResponse(BaseModel):
    name: str
    count: float


# ============================================================
# AUTHOR DETAIL
# ============================================================

class AuthorDetailResponse(BaseModel):
    id: str
    name: str
    orcid: Optional[str] = None
    works_count: int
    cited_by_count: int
    h_index: Optional[int] = None
    institution: Optional[str] = None
    country: Optional[str] = None
    topics: List[ResearchTopicResponse]


# ============================================================
# INSTITUTION SEARCH
# ============================================================

class InstitutionSearchItem(BaseModel):
    id: str
    name: str
    country: Optional[str] = None
    works_count: int
    cited_by_count: int


class InstitutionSearchResponse(BaseModel):
    count: int
    results: List[InstitutionSearchItem]


# ============================================================
# INSTITUTION DETAIL
# ============================================================

class InstitutionAuthorResponse(BaseModel):
    name: str


class InstitutionTopicResponse(BaseModel):
    name: str
    count: float


class InstitutionDetailResponse(BaseModel):
    id: str
    name: str
    country: Optional[str] = None
    homepage_url: Optional[str] = None
    works_count: int
    cited_by_count: int
    topics: List[InstitutionTopicResponse]
    top_authors: List[InstitutionAuthorResponse]


# ============================================================
# RECOMMENDATIONS
# ============================================================

class RecommendationItem(BaseModel):
    title: str
    authors: List[str]
    publication_year: Optional[int] = None
    cited_by_count: int
    doi: Optional[str] = None
    url: Optional[str] = None


class RecommendationResponse(BaseModel):
    query: str
    recommendations: List[RecommendationItem]


# ============================================================
# AI RESEARCH SUMMARY
# ============================================================

class ResearchSummaryRequest(BaseModel):
    title: str
    abstract: str


class InnovationOpportunity(BaseModel):
    strategy_name: str
    description: str


class ResearchSummaryResponse(BaseModel):
    summary: str
    objective: str
    methodology: str
    key_findings: str
    future_scope: str

    innovation_opportunities: List[
        Union[str, InnovationOpportunity]
    ]


# ============================================================
# AI INNOVATION GENERATOR
# ============================================================

class InnovationGeneratorRequest(BaseModel):
    title: str
    abstract: str


class StartupIdea(BaseModel):
    startup_name: str
    description: str
    target_customers: str
    revenue_model: str


class ProductIdea(BaseModel):
    product_name: str
    description: str


class IndustryApplication(BaseModel):
    industry: str
    application: str


class BusinessModel(BaseModel):
    model: str
    reason: str


class PatentOpportunity(BaseModel):
    title: str
    novelty: str


class MarketAnalysis(BaseModel):
    market_size: str
    competition: str
    growth_potential: str


class TechnologyReadiness(BaseModel):
    trl: str
    reason: str


class CommercializationPlan(BaseModel):
    first_step: str
    partners: str
    timeline: str


class InnovationGeneratorResponse(BaseModel):
    problem_statement: str

    startup_ideas: List[StartupIdea]

    product_ideas: List[ProductIdea]

    industry_applications: List[IndustryApplication]

    business_models: List[BusinessModel]

    patent_opportunities: List[PatentOpportunity]

    market_analysis: MarketAnalysis

    technology_readiness: TechnologyReadiness

    commercialization_plan: CommercializationPlan


# ============================================================
# AI RESEARCH GAP DETECTOR
# ============================================================

class ResearchGapRequest(BaseModel):
    title: str
    abstract: str


class ResearchGapResponse(BaseModel):
    limitations: List[str]
    research_gaps: List[str]
    future_directions: List[str]
    novel_opportunities: List[str]
    interdisciplinary_opportunities: List[str]


# ============================================================
# AI LITERATURE REVIEW
# ============================================================

class LiteratureReviewRequest(BaseModel):
    title: str
    abstract: str


class ExistingResearch(BaseModel):
    title: str
    year: Optional[int] = None
    abstract: str


class KeyTechnique(BaseModel):
    technique: str
    description: str


class ResearchChallenge(BaseModel):
    challenge: str
    description: str


class ComparisonItem(BaseModel):
    methodology: str
    advantages: str
    disadvantages: str


class LiteratureReviewResponse(BaseModel):
    overview: str

    existing_research: List[ExistingResearch]

    key_techniques: List[KeyTechnique]

    research_challenges: List[ResearchChallenge]

    comparison: List[ComparisonItem]

    conclusion: str


# ============================================================
# AI RESEARCH TREND ANALYZER
# ============================================================

class ResearchTrendRequest(BaseModel):
    title: str
    abstract: str


class TrendingTopic(BaseModel):
    topic: str
    reason: str


class EmergingKeyword(BaseModel):
    keyword: str
    importance: str


class FutureTrend(BaseModel):
    trend: str
    impact: str


class ResearchTrendResponse(BaseModel):
    trending_topics: List[TrendingTopic]
    emerging_keywords: List[EmergingKeyword]
    future_trends: List[FutureTrend]
    publication_growth: str
    recommendation: str


# ============================================================
# CITATION INTELLIGENCE
# ============================================================

class CitationRequest(BaseModel):
    title: str
    authors: List[str]
    journal: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None


class CitationResponse(BaseModel):
    apa: str
    ieee: str
    mla: str
    chicago: str
    bibtex: str
    ris: str


# ============================================================
# AI RESEARCH CHAT
# ============================================================

class ResearchChatRequest(BaseModel):
    title: str
    abstract: str
    question: str


class ResearchChatResponse(BaseModel):
    answer: str


# ============================================================
# PAPER COMPARATOR
# ============================================================

class PaperComparatorRequest(BaseModel):
    title1: str
    abstract1: str
    title2: str
    abstract2: str


class PaperComparatorResponse(BaseModel):
    similarities: List[str]
    differences: List[str]
    strengths_paper1: List[str]
    strengths_paper2: List[str]
    weaknesses_paper1: List[str]
    weaknesses_paper2: List[str]
    recommendation: str


# ============================================================
# RESEARCH PROPOSAL
# ============================================================

class ResearchProposalRequest(BaseModel):
    title: str
    abstract: str


class ResearchProposalResponse(BaseModel):
    problem_statement: str
    objectives: List[str]
    literature_review: str
    methodology: str
    expected_outcomes: List[str]
    future_scope: str
    timeline: str


# ============================================================
# NOVELTY CHECKER
# ============================================================

class NoveltyCheckerRequest(BaseModel):
    title: str
    abstract: str


class NoveltyCheckerResponse(BaseModel):
    novelty_score: int
    innovation_level: str
    uniqueness: str
    similar_research: List[str]
    unique_contributions: List[str]
    patent_potential: str
    improvement_suggestions: List[str]


# ============================================================
# RESEARCH QUESTION GENERATOR
# ============================================================

class ResearchQuestionRequest(BaseModel):
    title: str
    abstract: str


class ResearchQuestionResponse(BaseModel):
    research_questions: List[str]
    objectives: List[str]
    hypotheses: List[str]
    research_scope: str
    future_research_directions: List[str]


# ============================================================
# METHODOLOGY RECOMMENDER
# ============================================================

class MethodologyRequest(BaseModel):
    title: str
    abstract: str


class MethodologyResponse(BaseModel):
    recommended_methodology: str
    algorithms: List[str]
    datasets: List[str]
    tools_frameworks: List[str]
    evaluation_metrics: List[str]
    experimental_setup: str
    validation_techniques: List[str]