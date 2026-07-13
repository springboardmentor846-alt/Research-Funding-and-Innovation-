from app.services.logging_service import LoggingService
logger = LoggingService()
from fastapi import APIRouter
from app.services.openalex_service import OpenAlexService
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.semantic_service import SemanticScholarService

semantic = SemanticScholarService()
from app.services.logging_service import LoggingService

logger = LoggingService()
from app.services.collaboration_network_service import CollaborationNetworkService

network = CollaborationNetworkService()



from app.services.research_gap_service import ResearchGapService

research_gap_service = ResearchGapService()

from app.services.similarity_service import SimilarityService

similarity_service = SimilarityService()
from app.services.organization_ranking_service import OrganizationRankingService

organization = OrganizationRankingService()
from app.services.research_impact_service import ResearchImpactService

impact = ResearchImpactService()
from app.services.topic_model_service import TopicModelService
from app.models.research_paper import ResearchPaper
from app.services.dashboard_service import DashboardService

dashboard = DashboardService()
from app.services.trend_forecast_service import TrendForecastService

trend_forecast = TrendForecastService()
from app.services.collaboration_service import CollaborationService

collaboration = CollaborationService()
topic_service = TopicModelService()
from app.services.ner_service import NERService

ner = NERService()
from app.services.opportunity_service import OpportunityService

opportunity = OpportunityService()
from app.services.trl_service import TRLService

trl = TRLService()
from app.services.stackoverflow_service import StackOverflowService

stackoverflow = StackOverflowService()

from app.services.github_service import GitHubService

github = GitHubService()


from app.services.funding_success_service import FundingSuccessService

funding_success_service = FundingSuccessService()
from app.services.recommendation_service import RecommendationService

from app.services.patent_landscape_service import PatentLandscapeService
from app.services.cache_service import CacheService

cache = CacheService()
patent_landscape = PatentLandscapeService()
recommendation = RecommendationService()
from app.services.adoption_service import AdoptionService
from app.services.scibert_service import SciBERTService

scibert = None
from app.services.dashboard_service import DashboardService
from app.services.productivity_service import ProductivityService

productivity = ProductivityService()
from app.services.competitive_service import CompetitiveService

competitive = CompetitiveService()
from app.database import get_db
from app.models.research_paper import ResearchPaper
from app.services.funding_ai_service import FundingAIService
dashboard = DashboardService()
funding_ai = FundingAIService()


router = APIRouter(
    prefix="/technology-ai",
    tags=["Technology AI"]
)

service = OpenAlexService()


@router.get("/openalex/{keyword}")
async def search_openalex(keyword: str):
    return await service.search(keyword)

@router.post("/sync/openalex/{keyword}")
async def sync_openalex(
    keyword: str,
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            f"Started OpenAlex synchronization for keyword: {keyword}"
        )

        papers = await service.search(keyword)

        saved = 0

        for paper in papers["results"]:

            openalex_id = paper.get("id")

            existing = db.query(
                ResearchPaper
            ).filter(
                ResearchPaper.openalex_id == openalex_id
            ).first()

            if existing:
                continue

            authors = ", ".join(
                [
                    author["author"]["display_name"]
                    for author in paper.get("authorships", [])
                ]
            )

            journal = ""

            if paper.get("primary_location"):

                source = paper["primary_location"].get("source")

                if source:

                    journal = source.get(
                        "display_name",
                        ""
                    )

            new_paper = ResearchPaper(

                openalex_id=openalex_id,

                title=paper.get("title"),

                abstract="",

                publication_year=paper.get(
                    "publication_year"
                ),

                citation_count=paper.get(
                    "cited_by_count"
                ),

                doi=paper.get("doi"),

                journal=journal,

                authors=authors,

                institutions="",

                research_domain=keyword

            )

            db.add(new_paper)

            saved += 1

        db.commit()

        logger.info(
            f"{saved} papers stored successfully for keyword: {keyword}"
        )

        return {

            "success": True,

            "saved": saved,

            "total_received": len(papers["results"])

        }

    except Exception as e:

        db.rollback()

        logger.error(
            f"OpenAlex Sync Error: {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
@router.get("/papers")
def get_papers(
    db: Session = Depends(get_db)
):

    cached = cache.get("papers")

    if cached:

        return {
            "cached": True,
            "data": cached
        }
    logger.info("Fetching all research papers")
    papers = db.query(
        ResearchPaper
    ).all()

    result = []

    for paper in papers:

        result.append({

            "id": paper.id,

            "title": paper.title,

            "domain": paper.research_domain,

            "citations": paper.citation_count

        })

    cache.set(
        "papers",
        result
    )

    return {

        "cached": False,

        "data": result

    }
@router.get("/papers/top-cited")
def top_cited(db: Session = Depends(get_db)):
    return (
        db.query(ResearchPaper)
        .order_by(
            ResearchPaper.citation_count.desc()
        )
        .limit(20)
        .all()
    )

@router.get("/papers/domain/{domain}")
def papers_by_domain(
    domain: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.research_domain.ilike(f"%{domain}%")
        )
        .all()
    )

@router.get("/semantic/{keyword}")
async def search_semantic(keyword: str):
    return await semantic.search(keyword)

@router.post("/bertopic/train")
def train_topics(
    db: Session = Depends(get_db)
):

    papers = db.query(ResearchPaper).all()

    documents = [
        paper.title
        for paper in papers
        if paper.title
    ]

    if len(documents) < 5:
        return {
            "success": False,
            "message": "Need at least 5 papers."
        }

    topic_service.train(documents)

    return {
        "success": True,
        "papers_used": len(documents)
    }

@router.get("/bertopic/topics")
def topics():

    return topic_service.topic_info().to_dict(
        orient="records"
    )

@router.get("/bertopic/topic/{topic_id}")
def topic(topic_id: int):

    return topic_service.get_topic(topic_id)

@router.post("/scibert/embed")
def generate_embeddings(
    db: Session = Depends(get_db)
):

    global scibert

    if scibert is None:
        scibert = SciBERTService()

    papers = db.query(ResearchPaper).all()

    updated = 0

    for paper in papers:

        if paper.title:

            paper.embedding = scibert.encode(
                paper.title
            )

            updated += 1

    db.commit()

    return {
        "embedded": updated
    }
@router.get("/scibert/similarity")
def similarity(
    text1: str,
    text2: str
):

    global scibert

    if scibert is None:
        scibert = SciBERTService()

    return {
        "similarity": scibert.similarity(
            text1,
            text2
        )
    }

@router.get("/ner/analyze/{paper_id}")
def analyze_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):

    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id
    ).first()

    if not paper:
        return {
            "success": False,
            "message": "Paper not found"
        }

    text = ""

    if paper.title:
        text += paper.title + " "

    if paper.abstract:
        text += paper.abstract

    entities = ner.extract(text)

    return {
        "paper": paper.title,
        "entities": entities
    }

@router.post("/ner/analyze-all")
def analyze_all(
    db: Session = Depends(get_db)
):

    papers = db.query(ResearchPaper).all()

    processed = 0

    for paper in papers:

        text = ""

        if paper.title:
            text += paper.title + " "

        if paper.abstract:
            text += paper.abstract

        entities = ner.extract(text)

        paper.keywords = ", ".join(
            entities["organizations"]
        )

        processed += 1

    db.commit()

    return {
        "processed": processed
    }

@router.get("/trl/statistics")
def trl_statistics(
    db: Session = Depends(get_db)
):

    stats = db.query(

        ResearchPaper.trl_level,

        func.count()

    ).group_by(

        ResearchPaper.trl_level

    ).all()

    return {

        "distribution": [

            {

                "trl": item[0],

                "count": item[1]

            }

            for item in stats

        ]
    }
@router.get("/trl/{paper_id}")
def analyze_trl(
    paper_id: int,
    db: Session = Depends(get_db)
):

    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id
    ).first()

    if not paper:
        return {
            "success": False,
            "message": "Paper not found"
        }

    text = ""

    if paper.title:
        text += paper.title + " "

    if paper.abstract:
        text += paper.abstract

    level = trl.detect(text)

    paper.trl_level = level

    db.commit()

    return {

        "paper": paper.title,

        "trl_level": level
    }

@router.post("/trl/analyze-all")
def analyze_all_trl(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Bulk TRL Analysis Started"
        )

        papers = db.query(
            ResearchPaper
        ).all()

        updated = 0

        for paper in papers:

            text = ""

            if paper.title:
                text += paper.title + " "

            if paper.abstract:
                text += paper.abstract

            paper.trl_level = trl.detect(text)

            updated += 1

        db.commit()

        logger.info(
            f"TRL Analysis Completed. Updated {updated} papers."
        )

        return {

            "success": True,

            "updated": updated

        }

    except Exception as e:

        db.rollback()

        logger.error(
            f"TRL Bulk Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
adoption = AdoptionService()


@router.post("/github/update-all")
async def github_tracking(
    db: Session = Depends(get_db)
):

    try:

        logger.info("GitHub Repository Analysis Started")

        papers = db.query(
            ResearchPaper
        ).all()

        updated = 0

        for paper in papers:

            repo = await github.search(
                paper.title
            )

            if repo:

                paper.github_repo = repo["name"]

                paper.github_stars = repo["stars"]

                paper.github_forks = repo["forks"]

                paper.github_watchers = repo["watchers"]

                paper.adoption_score = adoption.score(

                    repo["stars"],

                    repo["forks"],

                    repo["watchers"]

                )

                updated += 1

        db.commit()

        logger.info(
            f"GitHub Repository Analysis Completed. Updated {updated} papers."
        )

        return {

            "success": True,

            "updated": updated

        }

    except Exception as e:

        db.rollback()

        logger.error(
            f"GitHub Update Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
@router.get("/github/top")
def github_top(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Fetching Top GitHub Projects"
        )

        papers = (

            db.query(

                ResearchPaper

            ).order_by(

                ResearchPaper.github_stars.desc()

            ).limit(10).all()

        )

        logger.info(
            f"{len(papers)} repositories fetched."
        )

        return {

            "success": True,

            "repositories": papers

        }

    except Exception as e:

        logger.error(
            f"GitHub Top Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
@router.get("/stackoverflow/{keyword}")
async def stackoverflow_search(keyword: str):

    data = await stackoverflow.search(keyword)

    if not data:
        return {
            "success": False,
            "message": "No Stack Overflow data found."
        }

    return {
        "total_questions": len(data),
        "questions": [
            {
                "title": q["title"],
                "score": q["score"],
                "views": q["view_count"],
                "answers": q["answer_count"],
                "tags": q["tags"]
            }
            for q in data
        ]
    }

@router.get("/opportunities")
def innovation_opportunities(
    db: Session = Depends(get_db)
):

    return {
        "count": len(opportunity.discover(db)),
        "results": opportunity.discover(db)
    }

@router.get("/recommend/{paper_id}")
def recommend_papers(
    paper_id: int,
    db: Session = Depends(get_db)
):

    return {
        "paper_id": paper_id,
        "recommendations": recommendation.recommend(
            db,
            paper_id
        )
    }

@router.get("/competitive/domains")
def competitive_domains(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Competitive Domain Analysis Started"
        )

        result = competitive.domain_statistics(db)

        logger.info(
            "Competitive Domain Analysis Completed"
        )

        return {

            "success": True,

            "domains": result

        }

    except Exception as e:

        logger.error(
            f"Competitive Domain Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()

@router.get("/patent-landscape")
def patent_landscape_analytics(
    db: Session = Depends(get_db)
):

    return patent_landscape.analytics(db)

@router.get("/collaboration/{profile_id}")
def collaboration_recommendation(
    profile_id: int,
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            f"Collaboration Recommendation Started for Profile {profile_id}"
        )

        recommendations = collaboration.recommend(
            db,
            profile_id
        )

        logger.info(
            f"Collaboration Recommendation Completed for Profile {profile_id}"
        )

        return {

            "success": True,

            "profile_id": profile_id,

            "recommendations": recommendations

        }

    except Exception as e:

        logger.error(
            f"Collaboration Recommendation Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
@router.get("/funding/recommend/{profile_id}")
def recommend_funding(
    profile_id: int,
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            f"Funding Recommendation Started for Profile {profile_id}"
        )

        recommendations = funding_ai.recommend(
            db,
            profile_id
        )

        logger.info(
            f"Funding Recommendation Completed for Profile {profile_id}"
        )

        return {

            "success": True,

            "profile_id": profile_id,

            "recommendations": recommendations

        }

    except Exception as e:

        logger.error(
            f"Funding Recommendation Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()
@router.get("/forecast/trends")
def forecast_trends(
    db: Session = Depends(get_db)
):

    return {

        "forecast":
            trend_forecast.forecast(db)

    }

@router.get("/dashboard")
def dashboard_api(

    db: Session = Depends(get_db)

):

    return {
    "overview": dashboard.overview(db),
    "publication_chart": dashboard.publication_chart(db),
    "citation_chart": dashboard.citation_chart(db),
    "trl_chart": dashboard.trl_chart(db),
    "domain_chart": dashboard.domain_chart(db),
    "funding_chart": dashboard.funding_chart(db)
}

@router.get("/analytics/research-impact")
def research_impact(
    db: Session = Depends(get_db)
):

    return {

        "researcher_rankings":
            impact.calculate(db)

    }
@router.get("/organization/ranking")
def organization_ranking(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Organization Ranking Requested"
        )

        result = organization.rankings(db)

        logger.info(
            "Organization Ranking Generated"
        )

        return {

            "success": True,

            "organizations": result

        }

    except Exception as e:

        logger.error(
            f"Organization Ranking Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()

@router.get("/analytics/collaboration-network")
def collaboration_network(
    db: Session = Depends(get_db)
):

    return {

        "network":

            network.network(db)

    }

@router.get("/productivity")
def research_productivity(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Research Productivity Analysis Started"
        )

        result = productivity.analyze(db)

        logger.info(
            "Research Productivity Analysis Completed"
        )

        return {

            "success": True,

            "productivity": result

        }

    except Exception as e:

        logger.error(
            f"Productivity Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()

@router.get("/funding/success")
def funding_success(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Funding Success Prediction Started"
        )

        result = funding_success_service.analyze(db)

        logger.info(
            "Funding Success Prediction Completed"
        )

        return {

            "success": True,

            "predictions": result

        }

    except Exception as e:

        logger.error(
            f"Funding Success Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()

@router.get("/analytics/similar-papers/{paper_id}")
def similar_papers(
    paper_id: int,
    db: Session = Depends(get_db)
):

    return {

        "paper_id": paper_id,

        "similar_papers":

            similarity_service.find_similar(
                db,
                paper_id
            )

    }

@router.get("/analytics/research-gap")
def research_gap(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Research Gap Analysis Started"
        )

        result = research_gap_service.analyze(db)

        logger.info(
            "Research Gap Analysis Completed"
        )

        return {

            "success": True,

            "data": result

        }

    except Exception as e:

        logger.error(
            f"Research Gap Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()

@router.get("/dashboard/overview")
def dashboard_overview(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Dashboard Overview Requested"
        )

        result = dashboard.overview(db)

        logger.info(
            "Dashboard Overview Generated"
        )

        return {

            "success": True,

            "data": result

        }

    except Exception as e:

        logger.error(
            f"Dashboard Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()


@router.get("/dashboard/publications")
def publication_chart(db: Session = Depends(get_db)):
    return dashboard.publication_chart(db)


@router.get("/dashboard/citations")
def citation_chart(db: Session = Depends(get_db)):
    return dashboard.citation_chart(db)


@router.get("/dashboard/trl")
def trl_chart(db: Session = Depends(get_db)):
    return dashboard.trl_chart(db)


@router.get("/dashboard/domains")
def domain_chart(db: Session = Depends(get_db)):
    return dashboard.domain_chart(db)


@router.get("/dashboard/funding")
def dashboard_funding(
    db: Session = Depends(get_db)
):

    try:

        logger.info(
            "Funding Dashboard Requested"
        )

        result = dashboard.funding_statistics(
            db
        )

        logger.info(
            "Funding Dashboard Generated"
        )

        return {

            "success": True,

            "data": result

        }

    except Exception as e:

        logger.error(
            f"Funding Dashboard Error : {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)

        }

    finally:

        db.close()