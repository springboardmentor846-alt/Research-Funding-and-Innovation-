from typing import List, Optional
from pydantic import BaseModel


# -----------------------------
# Author
# -----------------------------
class AuthorResponse(BaseModel):
    name: str


# -----------------------------
# Institution
# -----------------------------
class InstitutionResponse(BaseModel):
    name: str


# -----------------------------
# Research Paper
# -----------------------------
class PaperResponse(BaseModel):
    id: str
    title: str
    publication_year: Optional[int]
    doi: Optional[str]
    cited_by_count: int
    authors: List[AuthorResponse]


# -----------------------------
# Search Response
# -----------------------------
class PaperSearchResponse(BaseModel):
    count: int
    results: List[PaperResponse]


# -----------------------------
# Paper Detail Response
# -----------------------------
class PaperDetailResponse(BaseModel):
    id: str
    title: str
    publication_year: Optional[int]
    doi: Optional[str]
    cited_by_count: int
    abstract: Optional[str]
    journal: Optional[str]
    pdf_url: Optional[str]
    authors: List[AuthorResponse]
    institutions: List[InstitutionResponse]
    # -----------------------------
# Author Search Response
# -----------------------------
class AuthorSearchItem(BaseModel):
    id: str
    name: str
    orcid: Optional[str]
    works_count: int
    cited_by_count: int
    h_index: Optional[int]
    last_known_institution: Optional[str]


class AuthorSearchResponse(BaseModel):
    count: int
    results: List[AuthorSearchItem]
    # -----------------------------
# Topic
# -----------------------------
class ResearchTopicResponse(BaseModel):
    name: str
    count: float

# -----------------------------
# Author Detail Response
# -----------------------------
class AuthorDetailResponse(BaseModel):
    id: str
    name: str
    orcid: Optional[str]
    works_count: int
    cited_by_count: int
    h_index: Optional[int]
    institution: Optional[str]
    country: Optional[str]
    topics: List[ResearchTopicResponse]
    # -----------------------------
# Institution Search Response
# -----------------------------
class InstitutionSearchItem(BaseModel):
    id: str
    name: str
    country: Optional[str]
    works_count: int
    cited_by_count: int


class InstitutionSearchResponse(BaseModel):
    count: int
    results: List[InstitutionSearchItem]
    
    # -----------------------------
# Institution Detail Response
# -----------------------------
class InstitutionAuthorResponse(BaseModel):
    name: str


class InstitutionTopicResponse(BaseModel):
    name: str
    count: float


class InstitutionDetailResponse(BaseModel):
    id: str
    name: str
    country: Optional[str]
    homepage_url: Optional[str]
    works_count: int
    cited_by_count: int
    topics: List[InstitutionTopicResponse]
    top_authors: List[InstitutionAuthorResponse]
    # -----------------------------
# Recommendation Response
# -----------------------------
class RecommendationItem(BaseModel):
    title: str
    authors: List[str]
    publication_year: Optional[int]
    cited_by_count: int
    doi: Optional[str]
    url: Optional[str]


class RecommendationResponse(BaseModel):
    query: str
    recommendations: List[RecommendationItem]
    # ============================================
# AI Research Summarizer
# ============================================

class ResearchSummaryRequest(BaseModel):
    title: str
    abstract: str


class ResearchSummaryResponse(BaseModel):
    summary: str
    objective: str
    methodology: str
    key_findings: str
    future_scope: str
    innovation_opportunities: List[str]
 


# ============================================
# AI Innovation Generator
# ============================================

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
    # ============================================
# AI Research Gap Detector
# ============================================

class ResearchGapRequest(BaseModel):
    title: str
    abstract: str


class ResearchGapResponse(BaseModel):
    limitations: List[str]
    research_gaps: List[str]
    future_directions: List[str]
    novel_opportunities: List[str]
    interdisciplinary_opportunities: List[str]
    # ============================================
# AI Literature Review Generator
# ============================================

class LiteratureReviewRequest(BaseModel):
    title: str
    abstract: str


# ============================================
# AI Literature Review Generator
# ============================================

class LiteratureReviewRequest(BaseModel):
    title: str
    abstract: str


class ExistingResearch(BaseModel):
    title: str
    year: Optional[int]
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
    # ============================================
# AI Research Trend Analyzer
# ============================================

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
    # ============================================
# Citation Intelligence
# ============================================

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
    # ============================================
# AI Research Chat Assistant
# ============================================

class ResearchChatRequest(BaseModel):
    title: str
    abstract: str
    question: str


class ResearchChatResponse(BaseModel):
    answer: str
    # ============================================
# Research Paper Comparator
# ============================================

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
    # ============================================
# Research Proposal Generator
# ============================================

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
    # ============================================
# Novelty Checker
# ============================================

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
    # ============================================
# Research Question Generator
# ============================================

class ResearchQuestionRequest(BaseModel):
    title: str
    abstract: str


class ResearchQuestionResponse(BaseModel):
    research_questions: List[str]
    objectives: List[str]
    hypotheses: List[str]
    research_scope: str
    future_research_directions: List[str]
    # ============================================
# Methodology Recommender
# ============================================

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