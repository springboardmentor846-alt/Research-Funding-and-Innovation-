print("✅ research_intelligence_routes.py loaded")
from fastapi import APIRouter, Query

from app.schemas.research_intelligence_schema import PaperSearchResponse
from app.services.research_intelligence_service import search_papers
from app.schemas.research_intelligence_schema import (
    PaperSearchResponse,
    PaperDetailResponse,
    
)

from app.services.research_intelligence_service import (
    search_papers,
    get_paper_details,
)
from app.schemas.research_intelligence_schema import (
    PaperSearchResponse,
    PaperDetailResponse,
    AuthorSearchResponse,
)

from app.services.research_intelligence_service import (
    search_papers,
    get_paper_details,
    search_authors,
)
from app.schemas.research_intelligence_schema import (
    PaperSearchResponse,
    PaperDetailResponse,
    AuthorSearchResponse,
    AuthorDetailResponse,
    InstitutionSearchResponse,
    InstitutionDetailResponse,
    RecommendationResponse,
    ResearchSummaryRequest,
ResearchSummaryResponse,
InnovationGeneratorRequest,
InnovationGeneratorResponse,
ResearchGapRequest,
ResearchGapResponse,LiteratureReviewRequest,
LiteratureReviewResponse,ResearchTrendRequest,
ResearchTrendResponse,CitationRequest,
CitationResponse,ResearchChatRequest,
ResearchChatResponse,PaperComparatorRequest,
PaperComparatorResponse,ResearchProposalRequest,
ResearchProposalResponse,NoveltyCheckerRequest,
NoveltyCheckerResponse,ResearchQuestionRequest,
ResearchQuestionResponse,MethodologyRequest,
MethodologyResponse
)

from app.services.research_intelligence_service import (
    search_papers,
    get_paper_details,
    search_authors,
    get_author_details,
    search_institutions,
    get_institution_details,
    get_recommendations,
    generate_research_summary,
    generate_research_innovation,
    detect_research_gap_service,generate_literature_review_service,
    analyze_research_trends_service,citation_intelligence,research_chat_assistant,
    paper_comparator,research_proposal_generator,novelty_checker,
    research_question_generator,methodology_recommender
)
router = APIRouter(
    prefix="/research-intelligence",
    tags=["Research Intelligence"]
)


@router.get(
    "/search-papers",
    response_model=PaperSearchResponse
)
def search_research_papers(
    query: str = Query(..., description="Search keyword"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=25),
):
    """
    Search research papers from OpenAlex.
    """
    return search_papers(
        query=query,
        page=page,
        per_page=per_page
    )
@router.get(
    "/paper/{paper_id}",
    response_model=PaperDetailResponse
)
def paper_details(paper_id: str):
    """
    Get complete details of a research paper.
    """
    return get_paper_details(paper_id)
@router.get(
    "/search-authors",
    response_model=AuthorSearchResponse
)
def search_research_authors(
    query: str = Query(..., description="Author name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=25),
):
    """
    Search authors using OpenAlex.
    """
    return search_authors(
        query=query,
        page=page,
        per_page=per_page,
    )
@router.get(
    "/author/{author_id}",
    response_model=AuthorDetailResponse
)
def author_details(author_id: str):
    """
    Get complete author details.
    """
    return get_author_details(author_id)
@router.get(
    "/search-institutions",
    response_model=InstitutionSearchResponse,
)
def search_research_institutions(
    query: str = Query(..., description="Institution name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=25),
):
    """
    Search institutions using OpenAlex.
    """
    return search_institutions(
        query=query,
        page=page,
        per_page=per_page,
    )
@router.get(
    "/institution/{institution_id}",
    response_model=InstitutionDetailResponse,
)
def institution_details(institution_id: str):
    """
    Get complete institution details.
    """
    return get_institution_details(institution_id)
@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
)
def research_recommendations(
    query: str = Query(..., description="Research topic"),
    limit: int = Query(10, ge=1, le=20),
):
    """
    Get recommended research papers.
    """
    return get_recommendations(
        query=query,
        limit=limit,
    )
@router.post(
    "/summarize",
    response_model=ResearchSummaryResponse,
    summary="Generate AI Research Summary"
)
def summarize_paper(request: ResearchSummaryRequest):
    """
    Generate an AI-powered summary for a research paper using Ollama.
    """

    return generate_research_summary(
        title=request.title,
        abstract=request.abstract
    )
# ============================================
# AI Innovation Generator
# ============================================

@router.post(
    "/generate-innovation",
    response_model=InnovationGeneratorResponse
)
def generate_innovation_route(
    request: InnovationGeneratorRequest
):
    return generate_research_innovation(
        request.title,
        request.abstract
    )
@router.post(
    "/research-gap-detector",
    response_model=ResearchGapResponse,
    summary="AI Research Gap Detector"
)
def research_gap_detector(request: ResearchGapRequest):
    """
    Detect research gaps, limitations,
    future directions and opportunities.
    """

    result = detect_research_gap_service(
        request.title,
        request.abstract
    )

    return result
@router.post(
    "/literature-review",
    response_model=LiteratureReviewResponse,
    summary="AI Literature Review Generator"
)
def literature_review(request: LiteratureReviewRequest):
    """
    Generate a structured literature review.
    """

    result = generate_literature_review_service(
        request.title,
        request.abstract
    )

    return result
# ============================================
# AI Research Trend Analyzer
# ============================================

@router.post(
    "/research-trends",
    response_model=ResearchTrendResponse
)
def research_trends(request: ResearchTrendRequest):
    """
    Analyze research trends using AI.
    """

    return analyze_research_trends_service(
        request.title,
        request.abstract
    )
@router.post(
    "/citation-intelligence",
    response_model=CitationResponse
)
def generate_citation(request: CitationRequest):

    return citation_intelligence(
        title=request.title,
        authors=request.authors,
        journal=request.journal,
        publication_year=request.publication_year,
        doi=request.doi
    )
@router.post(
    "/research-chat",
    response_model=ResearchChatResponse
)
def research_chat_endpoint(
    request: ResearchChatRequest
):

    return research_chat_assistant(
        title=request.title,
        abstract=request.abstract,
        question=request.question
    )
@router.post(
    "/paper-comparator",
    response_model=PaperComparatorResponse
)
def compare_papers(request: PaperComparatorRequest):

    return paper_comparator(
        request.title1,
        request.abstract1,
        request.title2,
        request.abstract2
    )
@router.post(
    "/research-proposal",
    response_model=ResearchProposalResponse
)
def generate_proposal(
    request: ResearchProposalRequest
):

    return research_proposal_generator(
        request.title,
        request.abstract
    )
@router.post(
    "/novelty-checker",
    response_model=NoveltyCheckerResponse
)
def novelty_checker_endpoint(
    request: NoveltyCheckerRequest
):

    return novelty_checker(
        request.title,
        request.abstract
    )
@router.post(
    "/research-question-generator",
    response_model=ResearchQuestionResponse
)
def generate_questions(
    request: ResearchQuestionRequest
):

    return research_question_generator(
        request.title,
        request.abstract
    )
@router.post(
    "/methodology-recommender",
    response_model=MethodologyResponse
)
def recommend_methodology_endpoint(
    request: MethodologyRequest
):

    return methodology_recommender(
        request.title,
        request.abstract
    )