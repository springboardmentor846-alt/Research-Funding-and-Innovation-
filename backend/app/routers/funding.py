from datetime import date, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy import (
    or_,
    select,
)

from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    require_role,
)

from app.models.funding import FundingOpportunity
from app.models.user import User

from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea

from app.schemas.funding import (
    FundingOpportunityCreate,
    FundingOpportunityUpdate,
)

from app.services.ai_service import (
    build_researcher_text,
    build_funding_text,
    rank_recommendations,
)

from app.services.funding_eligibility_service import (
    check_funding_eligibility,
)

from app.services.funding_collection_service import (
    save_funding_opportunities,
)

from app.services.funding_source_service import (
    collect_funding_sources,
)


router = APIRouter(
    prefix="/funding",
    tags=["Funding Opportunities"],
)


# ============================================================
# HELPER
# ============================================================

def funding_to_dict(funding):

    return {

        "id":
            funding.id,

        "title":
            funding.title,

        "organization":
            funding.organization,

        "funding_type":
            funding.funding_type,

        "research_domain":
            funding.research_domain,

        "description":
            funding.description,

        "funding_amount":
            funding.funding_amount,

        "deadline":
            funding.deadline,

        "official_link":
            funding.official_link,

        "country":
            funding.country,

        "eligible_countries":
            funding.eligible_countries,

        "international_applicants_allowed":
            funding.international_applicants_allowed,

        "career_stage":
            funding.career_stage,

        "qualification":
            funding.qualification,

        "experience_required":
            funding.experience_required,

        "keywords":
            funding.keywords,

        "status":
            funding.status,
    }


# ============================================================
# CREATE FUNDING OPPORTUNITY
# ADMINISTRATOR ONLY
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_funding_opportunity(

    funding_data: FundingOpportunityCreate,

    current_user: User = Depends(
        require_role("administrator")
    ),

    db: Session = Depends(get_db),
):

    existing = db.scalar(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.title
            == funding_data.title,

            FundingOpportunity.organization
            == funding_data.organization,
        )
    )

    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Funding opportunity already exists",
        )

    funding = FundingOpportunity(
        **funding_data.model_dump()
    )

    db.add(funding)
    db.commit()
    db.refresh(funding)

    return {

        "message":
            "Funding opportunity created successfully",

        "funding_id":
            funding.id,

        "title":
            funding.title,
    }


# ============================================================
# GET ALL FUNDING OPPORTUNITIES
# ============================================================

@router.get("")
def get_all_funding(

    db: Session = Depends(get_db),
):

    funding_list = db.scalars(

        select(
            FundingOpportunity
        ).order_by(
            FundingOpportunity.id
        )

    ).all()

    return {

        "count":
            len(funding_list),

        "funding_opportunities": [

            funding_to_dict(
                funding
            )

            for funding
            in funding_list
        ],
    }


# ============================================================
# RULE-BASED PERSONALIZED RECOMMENDATIONS
#
# Keeping your existing rule-based recommendation
# separately so that you can compare rule-based vs AI.
# ============================================================

@router.get("/recommendations")
def get_funding_recommendations(

    current_user: User = Depends(
        require_role("researcher")
    ),

    db: Session = Depends(get_db),
):

    profile = db.scalar(

        select(
            ResearchProfile
        ).where(

            ResearchProfile.user_id
            == current_user.id
        )
    )

    if profile is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found",
        )

    research_domains = db.scalars(

        select(
            ResearchDomain
        ).where(

            ResearchDomain.research_profile_id
            == profile.id
        )

    ).all()

    keywords = db.scalars(

        select(
            ResearchKeyword
        ).where(

            ResearchKeyword.research_profile_id
            == profile.id
        )

    ).all()

    technology_areas = db.scalars(

        select(
            TechnologyArea
        ).where(

            TechnologyArea.research_profile_id
            == profile.id
        )

    ).all()

    funding_list = db.scalars(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.status
            == "Open"
        )

    ).all()

    recommended = []

    for funding in funding_list:

        score = 0

        # ------------------------------------------------------
        # DOMAIN MATCH
        # ------------------------------------------------------

        for domain in research_domains:

            if (
                funding.research_domain
                and domain.name
                and domain.name.lower()
                in funding.research_domain.lower()
            ):

                score += 40
                break

        # ------------------------------------------------------
        # KEYWORD MATCH
        # ------------------------------------------------------

        if funding.keywords:

            for keyword in keywords:

                if (
                    keyword.name
                    and keyword.name.lower()
                    in funding.keywords.lower()
                ):

                    score += 20
                    break

        # ------------------------------------------------------
        # TECHNOLOGY MATCH
        # ------------------------------------------------------

        if funding.keywords:

            for area in technology_areas:

                if (
                    area.name
                    and area.name.lower()
                    in funding.keywords.lower()
                ):

                    score += 25
                    break

        # ------------------------------------------------------
        # QUALIFICATION MATCH
        # ------------------------------------------------------

        if (
            funding.qualification
            and profile.highest_qualification
            and funding.qualification.lower()
            == profile.highest_qualification.lower()
        ):

            score += 10

        # ------------------------------------------------------
        # CAREER STAGE MATCH
        # ------------------------------------------------------

        if (
            funding.career_stage
            and profile.current_position
            and profile.current_position.lower()
            in funding.career_stage.lower()
        ):

            score += 5

        if score > 0:

            recommended.append({

                "funding_id":
                    funding.id,

                "title":
                    funding.title,

                "organization":
                    funding.organization,

                "research_domain":
                    funding.research_domain,

                "funding_amount":
                    funding.funding_amount,

                "deadline":
                    funding.deadline,

                "match_score":
                    score,
            })

    recommended.sort(

        key=lambda item:
            item["match_score"],

        reverse=True,
    )

    return {

        "research_profile_id":
            profile.id,

        "total_recommendations":
            len(recommended),

        "recommendations":
            recommended,
    }


# ============================================================
# AI / SEMANTIC PERSONALIZED FUNDING RECOMMENDATIONS
# + ELIGIBILITY MATCHING
# ============================================================

@router.get("/recommendations/ai")
def ai_funding_recommendations(

    current_user: User = Depends(
        require_role("researcher")
    ),

    db: Session = Depends(get_db),
):

    # ----------------------------------------------------------
    # 1. GET RESEARCH PROFILE
    # ----------------------------------------------------------

    profile = db.scalar(

        select(
            ResearchProfile
        ).where(

            ResearchProfile.user_id
            == current_user.id
        )
    )

    if profile is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found.",
        )

    # ----------------------------------------------------------
    # 2. RESEARCH DOMAINS
    # ----------------------------------------------------------

    domains = db.scalars(

        select(
            ResearchDomain
        ).where(

            ResearchDomain.research_profile_id
            == profile.id
        )

    ).all()

    # ----------------------------------------------------------
    # 3. KEYWORDS
    # ----------------------------------------------------------

    keywords = db.scalars(

        select(
            ResearchKeyword
        ).where(

            ResearchKeyword.research_profile_id
            == profile.id
        )

    ).all()

    # ----------------------------------------------------------
    # 4. TECHNOLOGY AREAS
    # ----------------------------------------------------------

    technologies = db.scalars(

        select(
            TechnologyArea
        ).where(

            TechnologyArea.research_profile_id
            == profile.id
        )

    ).all()

    # ----------------------------------------------------------
    # 5. BUILD PERSONALIZED RESEARCHER REPRESENTATION
    # ----------------------------------------------------------

    researcher_text = build_researcher_text(

        profile,
        domains,
        keywords,
        technologies,
    )

    # ----------------------------------------------------------
    # 6. GET OPEN FUNDING OPPORTUNITIES
    # ----------------------------------------------------------

    funding_list = db.scalars(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.status
            == "Open"
        )

    ).all()

    if not funding_list:

        return {

            "researcher":
                current_user.email,

            "research_profile_id":
                profile.id,

            "total_matches":
                0,

            "recommendations":
                [],
        }

    # ----------------------------------------------------------
    # 7. AI / SEMANTIC RANKING
    # ----------------------------------------------------------

    recommendations = rank_recommendations(

        researcher_text=
            researcher_text,

        items=
            funding_list,

        text_builder=
            build_funding_text,

        subtitle_field=
            "organization",
    )

    # ----------------------------------------------------------
    # 8. FUNDING LOOKUP MAP
    # ----------------------------------------------------------

    funding_map = {

        funding.id:
            funding

        for funding
        in funding_list
    }

    # ----------------------------------------------------------
    # 9. ENRICH RESULTS
    # ----------------------------------------------------------

    enriched_recommendations = []

    for recommendation in recommendations:

        funding_id = recommendation.get(
            "id"
        )

        funding = funding_map.get(
            funding_id
        )

        if funding is None:
            continue

        # ------------------------------------------------------
        # SIMILARITY SCORE
        # ------------------------------------------------------

        score = recommendation.get(
            "similarity_score",
            recommendation.get(
                "score",
                0,
            ),
        )

        # Convert 0-1 similarity to percentage

        if score <= 1:

            relevance_score = round(
                score * 100,
                2,
            )

        else:

            relevance_score = round(
                score,
                2,
            )

        # ------------------------------------------------------
        # HUMAN READABLE RELEVANCE
        # ------------------------------------------------------

        if relevance_score >= 70:

            relevance_level = (
                "Highly Relevant"
            )

        elif relevance_score >= 50:

            relevance_level = (
                "Relevant"
            )

        elif relevance_score >= 30:

            relevance_level = (
                "Moderate Match"
            )

        else:

            relevance_level = (
                "Low Match"
            )

        # ------------------------------------------------------
        # ELIGIBILITY ANALYSIS
        # ------------------------------------------------------

        eligibility = (
            check_funding_eligibility(
                profile,
                funding,
            )
        )

        # ------------------------------------------------------
        # FINAL RECOMMENDATION
        # ------------------------------------------------------

        enriched_recommendations.append({

            "id":
                funding.id,

            "title":
                funding.title,

            "organization":
                funding.organization,

            "funding_type":
                funding.funding_type,

            "research_domain":
                funding.research_domain,

            "description":
                funding.description,

            "funding_amount":
                funding.funding_amount,

            "deadline":
                funding.deadline,

            "official_link":
                funding.official_link,

            "country":
                funding.country,

            "eligible_countries":
                funding.eligible_countries,

            "international_applicants_allowed":
                funding.international_applicants_allowed,

            "career_stage":
                funding.career_stage,

            "qualification":
                funding.qualification,

            "experience_required":
                funding.experience_required,

            "keywords":
                funding.keywords,

            "status":
                funding.status,

            "relevance_score":
                relevance_score,

            "relevance_level":
                relevance_level,

            "eligibility":
                eligibility,
        })

    # ----------------------------------------------------------
    # 10. SORT BEST MATCH FIRST
    # ----------------------------------------------------------

    enriched_recommendations.sort(

        key=lambda item:
            item["relevance_score"],

        reverse=True,
    )

    return {

        "researcher":
            current_user.email,

        "research_profile_id":
            profile.id,

        "total_matches":
            len(
                enriched_recommendations
            ),

        "recommendations":
            enriched_recommendations,
    }


# ============================================================
# SEARCH / FILTER FUNDING
#
# IMPORTANT:
# This MUST stay ABOVE /{funding_id}
# ============================================================

@router.get("/search")
def search_funding_opportunities(

    query: str | None = Query(
        default=None
    ),

    domain: str | None = Query(
        default=None
    ),

    country: str | None = Query(
        default=None
    ),

    funding_type: str | None = Query(
        default=None
    ),

    funding_status: str | None = Query(
        default="Open"
    ),

    current_user: User = Depends(
        require_role("researcher")
    ),

    db: Session = Depends(get_db),
):

    statement = select(
        FundingOpportunity
    )

    # ----------------------------------------------------------
    # STATUS
    # ----------------------------------------------------------

    if funding_status:

        statement = statement.where(

            FundingOpportunity.status
            == funding_status
        )

    # ----------------------------------------------------------
    # GENERAL TEXT SEARCH
    # ----------------------------------------------------------

    if query:

        search_value = (
            f"%{query.strip()}%"
        )

        statement = statement.where(

            or_(

                FundingOpportunity.title.ilike(
                    search_value
                ),

                FundingOpportunity.description.ilike(
                    search_value
                ),

                FundingOpportunity.keywords.ilike(
                    search_value
                ),

                FundingOpportunity.organization.ilike(
                    search_value
                ),

                FundingOpportunity.research_domain.ilike(
                    search_value
                ),
            )
        )

    # ----------------------------------------------------------
    # DOMAIN
    # ----------------------------------------------------------

    if domain:

        statement = statement.where(

            FundingOpportunity.research_domain.ilike(
                f"%{domain.strip()}%"
            )
        )

    # ----------------------------------------------------------
    # COUNTRY
    # ----------------------------------------------------------

    if country:

        statement = statement.where(

            or_(

                FundingOpportunity.country.ilike(
                    f"%{country.strip()}%"
                ),

                FundingOpportunity.eligible_countries.ilike(
                    f"%{country.strip()}%"
                ),
            )
        )

    # ----------------------------------------------------------
    # FUNDING TYPE
    # ----------------------------------------------------------

    if funding_type:

        statement = statement.where(

            FundingOpportunity.funding_type.ilike(
                f"%{funding_type.strip()}%"
            )
        )

    opportunities = db.scalars(
        statement
    ).all()

    return {

        "count":
            len(opportunities),

        "funding_opportunities": [

            funding_to_dict(
                funding
            )

            for funding
            in opportunities
        ],
    }


# ============================================================
# FUNDING DEADLINE ALERTS
#
# IMPORTANT:
# Keep ABOVE /{funding_id}
# ============================================================

@router.get("/alerts")
def get_funding_alerts(

    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),

    current_user: User = Depends(
        require_role("researcher")
    ),

    db: Session = Depends(get_db),
):

    today = date.today()

    end_date = (
        today
        + timedelta(
            days=days
        )
    )

    opportunities = db.scalars(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.status
            == "Open",

            FundingOpportunity.deadline
            .is_not(None),

            FundingOpportunity.deadline
            >= today,

            FundingOpportunity.deadline
            <= end_date,
        ).order_by(

            FundingOpportunity.deadline
        )

    ).all()

    alerts = []

    for funding in opportunities:

        days_remaining = (
            funding.deadline
            - today
        ).days

        alerts.append({

            "id":
                funding.id,

            "title":
                funding.title,

            "organization":
                funding.organization,

            "funding_amount":
                funding.funding_amount,

            "deadline":
                funding.deadline,

            "days_remaining":
                days_remaining,

            "official_link":
                funding.official_link,
        })

    return {

        "alert_period_days":
            days,

        "count":
            len(alerts),

        "alerts":
            alerts,
    }


# ============================================================
# COLLECT / UPDATE FUNDING DATABASE
#
# ADMINISTRATOR ONLY
#
# IMPORTANT:
# Keep ABOVE /{funding_id}
# ============================================================

@router.post("/collect")
def collect_funding_opportunities(

    current_user: User = Depends(
        require_role("administrator")
    ),

    db: Session = Depends(get_db),
):

    records = (
        collect_funding_sources()
    )

    result = (
        save_funding_opportunities(
            db,
            records,
        )
    )

    return {

        "message":
            "Funding collection completed.",

        **result,
    }


# ============================================================
# GET ONE FUNDING OPPORTUNITY
#
# ALL STATIC ROUTES ABOVE THIS POINT.
# ============================================================

@router.get("/{funding_id}")
def get_funding_by_id(

    funding_id: int,

    db: Session = Depends(get_db),
):

    funding = db.scalar(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.id
            == funding_id
        )
    )

    if funding is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found",
        )

    result = funding_to_dict(
        funding
    )

    result["created_at"] = (
        funding.created_at
    )

    result["updated_at"] = (
        funding.updated_at
    )

    return result


# ============================================================
# UPDATE FUNDING OPPORTUNITY
# ADMINISTRATOR ONLY
# ============================================================

@router.patch("/{funding_id}")
def update_funding_opportunity(

    funding_id: int,

    funding_data:
        FundingOpportunityUpdate,

    current_user: User = Depends(
        require_role("administrator")
    ),

    db: Session = Depends(get_db),
):

    funding = db.scalar(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.id
            == funding_id
        )
    )

    if funding is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found",
        )

    update_data = (
        funding_data.model_dump(
            exclude_unset=True
        )
    )

    for field, value in (
        update_data.items()
    ):

        setattr(
            funding,
            field,
            value,
        )

    db.commit()
    db.refresh(funding)

    return {

        "message":
            "Funding opportunity updated successfully",

        "funding_id":
            funding.id,

        "updated_fields":
            list(
                update_data.keys()
            ),
    }


# ============================================================
# DELETE FUNDING OPPORTUNITY
# ADMINISTRATOR ONLY
# ============================================================

@router.delete("/{funding_id}")
def delete_funding_opportunity(

    funding_id: int,

    current_user: User = Depends(
        require_role("administrator")
    ),

    db: Session = Depends(get_db),
):

    funding = db.scalar(

        select(
            FundingOpportunity
        ).where(

            FundingOpportunity.id
            == funding_id
        )
    )

    if funding is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found",
        )

    deleted_title = (
        funding.title
    )

    db.delete(
        funding
    )

    db.commit()

    return {

        "message":
            "Funding opportunity deleted successfully",

        "deleted_funding":
            deleted_title,
    }