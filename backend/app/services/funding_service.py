"""
Service layer for Funding Opportunities, Bookmarks, Alerts, Search, and AI Recommendations.
"""
import logging
import math
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.funding import FundingOpportunity, FundingBookmark, FundingAlert
from app.models.research_profile import ResearchProfile
from app.schemas.funding import (
    FundingOpportunityCreate,
    FundingOpportunityUpdate,
    FundingOpportunityResponse,
    FundingOpportunityListResponse,
    FundingBookmarkResponse,
    FundingAlertCreate,
    FundingAlertUpdate,
    FundingAlertResponse,
    FundingRecommendationResponse,
    FundingDashboardSummaryResponse,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Similarity & Recommendation Scoring Logic
# Prepared for future Sentence Transformer integration
# ──────────────────────────────────────────────────────────────────────────────
def _compute_similarity_score(
    profile_domains: List[str],
    profile_keywords: List[str],
    profile_tech: List[str],
    profile_bio: Optional[str],
    opportunity: FundingOpportunity,
) -> Tuple[float, List[str], List[str]]:
    """
    Computes match score (0.0 to 100.0) and lists matching terms.
    
    FUTURE EXTENSION POINT:
    Replace token set intersection below with SentenceTransformer embedding dot product:
    `score = cos_sim(model.encode(profile_text), model.encode(opportunity_text))`
    """
    profile_domain_set = {d.lower().strip() for d in profile_domains if d}
    profile_kw_set = {
        k.lower().strip()
        for k in (profile_keywords + profile_tech)
        if k
    }
    
    if profile_bio:
        profile_kw_set.update({w.lower().strip() for w in profile_bio.split() if len(w) > 3})

    opp_domain_set = {d.lower().strip() for d in (opportunity.research_domains or [])}
    opp_kw_set = {k.lower().strip() for k in (opportunity.keywords or [])}

    matched_domains = list(profile_domain_set.intersection(opp_domain_set))
    matched_kws = list(profile_kw_set.intersection(opp_kw_set))

    # Also check if keywords appear in title or description
    opp_text = f"{opportunity.title} {opportunity.description}".lower()
    for kw in profile_kw_set:
        if kw and kw not in matched_kws and kw in opp_text:
            matched_kws.append(kw)

    # Weighted scoring
    domain_score = (len(matched_domains) / max(len(profile_domain_set), 1)) * 50.0
    kw_score = (len(matched_kws) / max(len(profile_kw_set), 1)) * 50.0

    raw_score = domain_score + kw_score

    # Baseline bonus for matching primary funder domain
    if matched_domains or matched_kws:
        raw_score += 15.0

    final_score = min(max(round(raw_score, 1), 10.0), 99.0)

    # If no profile data exists, provide a default baseline
    if not profile_domains and not profile_keywords and not profile_tech:
        final_score = 50.0

    return final_score, matched_kws[:5], matched_domains[:5]


class FundingService:

    @staticmethod
    async def get_opportunity_by_id(
        db: AsyncSession, opportunity_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> FundingOpportunityResponse:
        stmt = select(FundingOpportunity).where(FundingOpportunity.id == opportunity_id)
        result = await db.execute(stmt)
        opp = result.scalar_one_or_none()
        if not opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Funding opportunity not found"
            )

        is_bm = False
        if user_id:
            bm_stmt = select(FundingBookmark).where(
                and_(
                    FundingBookmark.user_id == user_id,
                    FundingBookmark.funding_opportunity_id == opportunity_id,
                )
            )
            bm_res = await db.execute(bm_stmt)
            is_bm = bm_res.scalar_one_or_none() is not None

        resp = FundingOpportunityResponse.model_validate(opp)
        resp.is_bookmarked = is_bm
        return resp

    @staticmethod
    async def search_opportunities(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        q: Optional[str] = None,
        domain: Optional[str] = None,
        funding_type: Optional[str] = None,
        country: Optional[str] = None,
        sort_by: str = "deadline_asc",
        page: int = 1,
        page_size: int = 12,
    ) -> FundingOpportunityListResponse:
        stmt = select(FundingOpportunity).where(FundingOpportunity.is_active == True)

        if q and q.strip():
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    FundingOpportunity.title.ilike(term),
                    FundingOpportunity.funder_name.ilike(term),
                    FundingOpportunity.description.ilike(term),
                )
            )

        if funding_type and funding_type.strip() and funding_type != "All":
            stmt = stmt.where(FundingOpportunity.funding_type.ilike(f"%{funding_type.strip()}%"))

        # Execute base query to fetch matching candidates for JSON filtering
        result = await db.execute(stmt)
        all_candidates = result.scalars().all()

        filtered = []
        for opp in all_candidates:
            # Domain filter
            if domain and domain.strip() and domain != "All":
                d_target = domain.strip().lower()
                opp_domains = [d.lower() for d in (opp.research_domains or [])]
                if not any(d_target in d for d in opp_domains):
                    continue

            # Country filter
            if country and country.strip() and country != "All":
                c_target = country.strip().lower()
                opp_countries = [c.lower() for c in (opp.eligible_countries or [])]
                if opp_countries and "global" not in opp_countries and not any(c_target in c for c in opp_countries):
                    continue

            filtered.append(opp)

        # Sorting
        now = datetime.now(timezone.utc)
        if sort_by == "deadline_asc":
            filtered.sort(key=lambda x: x.deadline if x.deadline else datetime.max.replace(tzinfo=timezone.utc))
        elif sort_by == "deadline_desc":
            filtered.sort(key=lambda x: x.deadline if x.deadline else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        elif sort_by == "amount_desc":
            filtered.sort(key=lambda x: (x.amount_max or 0), reverse=True)
        elif sort_by == "created_desc":
            filtered.sort(key=lambda x: x.created_at or now, reverse=True)

        total = len(filtered)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = filtered[start_idx:end_idx]

        # Get user bookmarks set
        user_bm_ids = set()
        if user_id:
            bm_stmt = select(FundingBookmark.funding_opportunity_id).where(
                FundingBookmark.user_id == user_id
            )
            bm_res = await db.execute(bm_stmt)
            user_bm_ids = set(bm_res.scalars().all())

        items = []
        for opp in paginated:
            resp = FundingOpportunityResponse.model_validate(opp)
            resp.is_bookmarked = opp.id in user_bm_ids
            items.append(resp)

        return FundingOpportunityListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_recommendations(
        db: AsyncSession, user_id: uuid.UUID, limit: int = 6
    ) -> List[FundingRecommendationResponse]:
        # Fetch user profile
        prof_stmt = select(ResearchProfile).where(ResearchProfile.user_id == user_id)
        prof_res = await db.execute(prof_stmt)
        profile = prof_res.scalar_one_or_none()

        profile_domains = profile.research_domains if profile else []
        profile_keywords = profile.keywords if profile else []
        profile_tech = profile.technology_interests if profile else []
        profile_bio = profile.summary_bio if profile else ""

        # Fetch active opportunities
        opp_stmt = select(FundingOpportunity).where(FundingOpportunity.is_active == True)
        opp_res = await db.execute(opp_stmt)
        opportunities = opp_res.scalars().all()

        # Fetch user bookmarks
        bm_stmt = select(FundingBookmark.funding_opportunity_id).where(
            FundingBookmark.user_id == user_id
        )
        bm_res = await db.execute(bm_stmt)
        user_bm_ids = set(bm_res.scalars().all())

        scored_items: List[FundingRecommendationResponse] = []
        for opp in opportunities:
            score, matched_kws, matched_domains = _compute_similarity_score(
                profile_domains, profile_keywords, profile_tech, profile_bio, opp
            )
            resp = FundingOpportunityResponse.model_validate(opp)
            resp.is_bookmarked = opp.id in user_bm_ids

            scored_items.append(
                FundingRecommendationResponse(
                    opportunity=resp,
                    match_score=score,
                    matched_keywords=matched_kws,
                    matched_domains=matched_domains,
                )
            )

        scored_items.sort(key=lambda x: x.match_score, reverse=True)
        return scored_items[:limit]

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession, user_id: uuid.UUID
    ) -> FundingDashboardSummaryResponse:
        recommendations = await FundingService.get_recommendations(db, user_id, limit=4)
        
        # Latest grants
        latest_res = await FundingService.search_opportunities(
            db, user_id=user_id, sort_by="created_desc", page=1, page_size=4
        )

        # Closing soon
        closing_res = await FundingService.search_opportunities(
            db, user_id=user_id, sort_by="deadline_asc", page=1, page_size=4
        )

        # Saved grants count
        bm_count_stmt = select(func.count(FundingBookmark.id)).where(FundingBookmark.user_id == user_id)
        bm_count_res = await db.execute(bm_count_stmt)
        saved_count = bm_count_res.scalar_one() or 0

        # Total count
        total_stmt = select(func.count(FundingOpportunity.id)).where(FundingOpportunity.is_active == True)
        total_res = await db.execute(total_stmt)
        total_count = total_res.scalar_one() or 0

        return FundingDashboardSummaryResponse(
            recommended_grants=recommendations,
            latest_grants=latest_res.items,
            closing_soon_grants=closing_res.items,
            saved_grants_count=saved_count,
            total_opportunities_count=total_count,
        )

    @staticmethod
    async def toggle_bookmark(
        db: AsyncSession, user_id: uuid.UUID, opportunity_id: uuid.UUID
    ) -> Dict[str, Any]:
        # Check opportunity exists
        opp_stmt = select(FundingOpportunity).where(FundingOpportunity.id == opportunity_id)
        opp_res = await db.execute(opp_stmt)
        if not opp_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Funding opportunity not found"
            )

        stmt = select(FundingBookmark).where(
            and_(
                FundingBookmark.user_id == user_id,
                FundingBookmark.funding_opportunity_id == opportunity_id,
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            await db.delete(existing)
            await db.commit()
            return {"bookmarked": False, "message": "Bookmark removed"}
        else:
            bm = FundingBookmark(user_id=user_id, funding_opportunity_id=opportunity_id)
            db.add(bm)
            await db.commit()
            return {"bookmarked": True, "message": "Bookmark added"}

    @staticmethod
    async def get_user_bookmarks(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[FundingOpportunityResponse]:
        stmt = (
            select(FundingBookmark)
            .where(FundingBookmark.user_id == user_id)
            .options(selectinload(FundingBookmark.opportunity))
            .order_by(desc(FundingBookmark.created_at))
        )
        result = await db.execute(stmt)
        bookmarks = result.scalars().all()

        items = []
        for bm in bookmarks:
            if bm.opportunity and bm.opportunity.is_active:
                resp = FundingOpportunityResponse.model_validate(bm.opportunity)
                resp.is_bookmarked = True
                items.append(resp)
        return items

    @staticmethod
    async def create_alert(
        db: AsyncSession, user_id: uuid.UUID, data: FundingAlertCreate
    ) -> FundingAlertResponse:
        alert = FundingAlert(user_id=user_id, **data.model_dump())
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return FundingAlertResponse.model_validate(alert)

    @staticmethod
    async def get_user_alerts(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[FundingAlertResponse]:
        stmt = (
            select(FundingAlert)
            .where(FundingAlert.user_id == user_id)
            .order_by(desc(FundingAlert.created_at))
        )
        result = await db.execute(stmt)
        alerts = result.scalars().all()
        return [FundingAlertResponse.model_validate(a) for a in alerts]

    @staticmethod
    async def delete_alert(db: AsyncSession, user_id: uuid.UUID, alert_id: uuid.UUID) -> None:
        stmt = select(FundingAlert).where(
            and_(FundingAlert.id == alert_id, FundingAlert.user_id == user_id)
        )
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Funding alert not found"
            )
        await db.delete(alert)
        await db.commit()

    @staticmethod
    async def create_opportunity(
        db: AsyncSession, data: FundingOpportunityCreate
    ) -> FundingOpportunityResponse:
        opp = FundingOpportunity(**data.model_dump())
        db.add(opp)
        await db.commit()
        await db.refresh(opp)
        return FundingOpportunityResponse.model_validate(opp)

    @staticmethod
    async def seed_funding_opportunities(db: AsyncSession) -> int:
        """Seed 50 realistic global funding opportunities if database is empty."""
        stmt = select(func.count(FundingOpportunity.id))
        result = await db.execute(stmt)
        count = result.scalar_one() or 0
        if count > 0:
            logger.info(f"Database already contains {count} funding opportunities. Skipping seed.")
            return count

        logger.info("Seeding 50 realistic funding opportunities...")
        now = datetime.now(timezone.utc)
        
        SEEDED_OPPORTUNITIES = [
            # 1
            {
                "title": "NSF Breakthrough Research in Artificial Intelligence & Quantum Information Systems",
                "funder_name": "National Science Foundation (NSF)",
                "funder_type": "Government",
                "description": "Supports foundational research in hybrid quantum-classical machine learning algorithms, scalable fault-tolerant quantum error correction, and ethical AI deployment for national defense and scientific computing.",
                "amount_min": 500000.0,
                "amount_max": 2500000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=45),
                "funding_type": "Grant",
                "eligible_countries": ["United States", "Global"],
                "research_domains": ["Artificial Intelligence", "Quantum Computing", "Computer Science"],
                "keywords": ["Quantum Machine Learning", "Qubits", "Fault-Tolerant Computing", "Neural Networks"],
                "application_url": "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505872",
            },
            # 2
            {
                "title": "Horizon Europe ERC Advanced Grant for Climate Action & Clean Energy Technologies",
                "funder_name": "European Research Council (ERC)",
                "funder_type": "Government",
                "description": "Funding for visionary research leaders pursuing groundbreaking energy storage breakthroughs, hydrogen fuel cells, carbon capture materials, and grid decarbonization models across EU and associated countries.",
                "amount_min": 1000000.0,
                "amount_max": 3500000.0,
                "currency": "EUR",
                "deadline": now + timedelta(days=90),
                "funding_type": "Grant",
                "eligible_countries": ["European Union", "United Kingdom", "Israel", "Norway"],
                "research_domains": ["Clean Energy", "Environmental Science", "Materials Science"],
                "keywords": ["Carbon Capture", "Battery Storage", "Hydrogen Fuel", "Grid Optimization"],
                "application_url": "https://erc.europa.eu/apply-grant/advanced-grant",
            },
            # 3
            {
                "title": "NIH Director's Transformative Research Award in Next-Gen Biotechnology & Genomics",
                "funder_name": "National Institutes of Health (NIH)",
                "funder_type": "Government",
                "description": "Supports high-risk, bold genomic engineering interventions, CRISPR-Cas13 mRNA editing platforms, synthetic cell therapies, and targeted cancer nanomedicine delivery systems.",
                "amount_min": 750000.0,
                "amount_max": 4000000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=60),
                "funding_type": "Grant",
                "eligible_countries": ["United States", "Global"],
                "research_domains": ["Biotechnology", "Genomics", "Medicine"],
                "keywords": ["CRISPR", "Gene Editing", "Cancer Nanomedicine", "Immunotherapy"],
                "application_url": "https://commonfund.nih.gov/tra",
            },
            # 4
            {
                "title": "DARPA Biological Technologies Office Innovation Seed Initiative",
                "funder_name": "Defense Advanced Research Projects Agency (DARPA)",
                "funder_type": "Government",
                "description": "Rapid response seed funding for neurotechnology interfaces, autonomous bio-manufacturing, synthetic biology bio-sensors, and human performance enhancement under extreme environments.",
                "amount_min": 250000.0,
                "amount_max": 1500000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=20),
                "funding_type": "Contract",
                "eligible_countries": ["United States"],
                "research_domains": ["Biotechnology", "Neuroscience", "Cybernetics"],
                "keywords": ["Brain-Computer Interface", "Synthetic Biology", "Bio-Sensors", "Neural Prosthetics"],
                "application_url": "https://www.darpa.mil/about-us/offices/bto",
            },
            # 5
            {
                "title": "Gates Foundation Global Health Discovery & Translation Grant",
                "funder_name": "Bill & Melinda Gates Foundation",
                "funder_type": "Foundation",
                "description": "Catalyzing solutions for infectious disease elimination, universal malaria vaccine platforms, low-cost diagnostic point-of-care biochips, and maternal nutrition in developing regions.",
                "amount_min": 100000.0,
                "amount_max": 1000000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=75),
                "funding_type": "Grant",
                "eligible_countries": ["Global", "India", "Kenya", "South Africa", "United States"],
                "research_domains": ["Medicine", "Public Health", "Biotechnology"],
                "keywords": ["Infectious Disease", "Vaccines", "Diagnostics", "Global Health"],
                "application_url": "https://www.gatesfoundation.org/how-we-work/general-information/grant-opportunities",
            },
            # 6
            {
                "title": "Y Combinator Bio & DeepTech Accelerator Spring Cohort",
                "funder_name": "Y Combinator",
                "funder_type": "Venture Capital",
                "description": "Investment funding, mentorship, and commercialization support for early-stage DeepTech startups building breakthrough novel physics, AI drug discovery, quantum hardware, and spacetech.",
                "amount_min": 500000.0,
                "amount_max": 500000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=15),
                "funding_type": "Equity",
                "eligible_countries": ["Global"],
                "research_domains": ["Artificial Intelligence", "Biotechnology", "Robotics", "DeepTech"],
                "keywords": ["Drug Discovery", "Startup Seed", "Commercialization", "Robotics"],
                "application_url": "https://www.ycombinator.com/apply",
            },
            # 7
            {
                "title": "Wellcome Trust Discovery Award for Fundamental Life Sciences",
                "funder_name": "Wellcome Trust",
                "funder_type": "Foundation",
                "description": "Funding for established researchers conducting bold, transformative exploration in structural biology, cellular aging pathways, cryo-EM protein dynamics, and host-pathogen interactions.",
                "amount_min": 800000.0,
                "amount_max": 3000000.0,
                "currency": "GBP",
                "deadline": now + timedelta(days=110),
                "funding_type": "Grant",
                "eligible_countries": ["United Kingdom", "Global"],
                "research_domains": ["Biochemistry", "Structural Biology", "Medicine"],
                "keywords": ["Cryo-EM", "Protein Dynamics", "Cellular Aging", "Host-Pathogen"],
                "application_url": "https://wellcome.org/grant-funding/schemes/discovery-awards",
            },
            # 8
            {
                "title": "Small Business Innovation Research (SBIR) Phase II in Autonomous Systems & Edge AI",
                "funder_name": "Department of Energy (DOE)",
                "funder_type": "Government",
                "description": "Commercialization grants for small businesses developing edge computing architectures, autonomous swarm robotics for nuclear monitoring, and ultra-efficient micro-semiconductors.",
                "amount_min": 1000000.0,
                "amount_max": 2000000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=35),
                "funding_type": "Grant",
                "eligible_countries": ["United States"],
                "research_domains": ["Robotics", "Computer Science", "Electrical Engineering"],
                "keywords": ["Edge AI", "Swarm Robotics", "Semiconductors", "Commercialization"],
                "application_url": "https://science.osti.gov/sbir",
            },
            # 9
            {
                "title": "UKRI Future Leaders Fellowship in Next-Gen Photonics & Semiconductors",
                "funder_name": "UK Research and Innovation (UKRI)",
                "funder_type": "Government",
                "description": "Long-term fellowship support for early and mid-career researchers pioneering optical computing chips, silicon photonics, high-power semiconductor lasers, and advanced manufacturing.",
                "amount_min": 400000.0,
                "amount_max": 1500000.0,
                "currency": "GBP",
                "deadline": now + timedelta(days=80),
                "funding_type": "Fellowship",
                "eligible_countries": ["United Kingdom", "European Union", "Global"],
                "research_domains": ["Physics", "Electrical Engineering", "Materials Science"],
                "keywords": ["Silicon Photonics", "Optical Computing", "Semiconductors", "Fellowship"],
                "application_url": "https://www.ukri.org/opportunity/future-leaders-fellowships",
            },
            # 10
            {
                "title": "Chan Zuckerberg Initiative Neurodegeneration Challenge Network Award",
                "funder_name": "Chan Zuckerberg Initiative (CZI)",
                "funder_type": "Foundation",
                "description": "Interdisciplinary team funding focused on solving Alzheimer's, Parkinson's, and ALS through single-cell spatial transcriptomics, neuroinflammation imaging, and biomarker discovery.",
                "amount_min": 600000.0,
                "amount_max": 2000000.0,
                "currency": "USD",
                "deadline": now + timedelta(days=105),
                "funding_type": "Grant",
                "eligible_countries": ["Global"],
                "research_domains": ["Neuroscience", "Genomics", "Medicine"],
                "keywords": ["Alzheimers", "Parkinsons", "Spatial Transcriptomics", "Neuroinflammation"],
                "application_url": "https://chanzuckerberg.com/science/programs-resources/neurodegeneration-challenge-network/",
            },
        ]

        # Generate 40 additional rich realistic variations to reach 50 opportunities
        domains_pool = [
            ("Cybersecurity & Zero Trust Architectures", "Department of Homeland Security (DHS)", "Government", "Computer Science", ["Zero Trust", "Cryptography", "Network Security", "Threat Intelligence"]),
            ("Agricultural Biotechnology & Climate Resilience", "US Department of Agriculture (USDA)", "Government", "Environmental Science", ["Crop Science", "Drought Resistance", "Soil Microbiome", "Food Security"]),
            ("Nanotechnology for Biomedical Imaging", "National Cancer Institute (NCI)", "Government", "Biotechnology", ["Nanoparticles", "MRI Contrast", "Fluorescence Imaging", "Targeted Therapy"]),
            ("Autonomous Electric Aircraft Propulsion Systems", "NASA Aeronautics Research Directorate", "Government", "Aerospace", ["eVTOL", "Electric Aviation", "Battery Densities", "Turbomachinery"]),
            ("Generative AI Models for Structural Biology & Protein Folding", "Schmid Futures AI Initiative", "Foundation", "Artificial Intelligence", ["Protein Folding", "AlphaFold", "Generative Models", "Molecular Docking"]),
            ("Ocean Decarbonization & Marine Biomass Capture", "Ocean Risk and Resilience Action Alliance", "Foundation", "Environmental Science", ["Blue Carbon", "Algae Biomass", "Ocean Acidification", "Marine Biology"]),
            ("Quantum Sensing & Atomic Clocks for Deep Space Navigation", "European Space Agency (ESA)", "Government", "Quantum Computing", ["Quantum Sensing", "Atomic Clocks", "Gravimetry", "Space Exploration"]),
            ("Advanced Robotics for Minimally Invasive Surgery", "Intuitive Surgical Research Grant", "Corporate", "Robotics", ["Surgical Robotics", "Haptic Feedback", "Endoscopy", "Medical Devices"]),
            ("Graphene & 2D Materials Commercialization Award", "Graphene Flagship Consortium", "Government", "Materials Science", ["Graphene", "2D Materials", "Flexible Electronics", "Supercapacitors"]),
            ("Synthetic Biology for Biodegradable Plastics", "Biotechnology Innovation Organization (BIO)", "Industry", "Biotechnology", ["Bioplastics", "Enzymatic Degradation", "Polymer Chemistry", "Circular Economy"]),
        ]

        for i in range(11, 51):
            tmpl = domains_pool[i % len(domains_pool)]
            deadline_days = 10 + (i * 3) % 120
            SEEDED_OPPORTUNITIES.append({
                "title": f"{tmpl[0]} Grant Cohort #{i}",
                "funder_name": tmpl[1],
                "funder_type": tmpl[2],
                "description": f"Global funding initiative focusing on {tmpl[0].lower()} to accelerate translational research, industrial pilot demonstrations, and interdisciplinary collaboration across academia and industry.",
                "amount_min": float(100000 + (i * 25000)),
                "amount_max": float(500000 + (i * 75000)),
                "currency": "USD" if i % 4 != 0 else "EUR",
                "deadline": now + timedelta(days=deadline_days),
                "funding_type": "Grant" if i % 3 != 0 else ("Contract" if i % 5 == 0 else "Fellowship"),
                "eligible_countries": ["Global", "United States", "European Union", "United Kingdom", "Canada", "Japan", "India"][:(i % 5 + 2)],
                "research_domains": [tmpl[3], "Engineering", "Technology"][:((i % 3) + 1)],
                "keywords": tmpl[4] + [f"Phase-{i%3+1}", "Innovation"],
                "application_url": f"https://example.org/funding/grant-{i}",
            })

        for opp_data in SEEDED_OPPORTUNITIES:
            opp = FundingOpportunity(**opp_data)
            db.add(opp)

        await db.commit()
        logger.info("Successfully seeded 50 realistic funding opportunities.")
        return 50
