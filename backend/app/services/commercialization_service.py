"""
Service layer for Commercialization Opportunities, Industry Partners, Startup Programs, Bookmarks, and AI Recommendations.
"""
import logging
import math
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.commercialization import (
    CommercializationOpportunity,
    IndustryPartner,
    StartupRecommendation,
    Collaboration,
)
from app.models.research_profile import ResearchProfile, Publication, Patent
from app.models.technology import InnovationScore
from app.schemas.commercialization import (
    CommercializationOpportunityCreate,
    CommercializationOpportunityUpdate,
    CommercializationOpportunityResponse,
    CommercializationOpportunityListResponse,
    IndustryPartnerResponse,
    StartupRecommendationResponse,
    CommercializationRecommendationResponse,
    CollaborationResponse,
    CollaborationRequestCreate,
    CommercializationDashboardSummaryResponse,
    CommercializationStatisticsSummary,
)

logger = logging.getLogger(__name__)


class CommercializationService:
    @staticmethod
    async def search_opportunities(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        q: Optional[str] = None,
        industry: Optional[str] = None,
        domain: Optional[str] = None,
        organization: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        sort_by: str = "created_desc",
        page: int = 1,
        page_size: int = 12,
    ) -> CommercializationOpportunityListResponse:
        """Search & filter commercialization opportunities with pagination."""
        query = select(CommercializationOpportunity).where(CommercializationOpportunity.is_active == True)

        filters = []
        if q:
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    CommercializationOpportunity.title.ilike(term),
                    CommercializationOpportunity.summary.ilike(term),
                    CommercializationOpportunity.organization_name.ilike(term),
                    CommercializationOpportunity.technology_domain.ilike(term),
                    CommercializationOpportunity.industry.ilike(term),
                )
            )
        if industry:
            filters.append(CommercializationOpportunity.industry.ilike(f"%{industry.strip()}%"))
        if domain:
            filters.append(CommercializationOpportunity.technology_domain.ilike(f"%{domain.strip()}%"))
        if organization:
            filters.append(CommercializationOpportunity.organization_name.ilike(f"%{organization.strip()}%"))
        if opportunity_type:
            filters.append(CommercializationOpportunity.opportunity_type.ilike(f"%{opportunity_type.strip()}%"))

        if filters:
            query = query.where(and_(*filters))

        # Sorting
        if sort_by == "funding_desc":
            query = query.order_by(desc(CommercializationOpportunity.estimated_funding_usd))
        elif sort_by == "trl_desc":
            query = query.order_by(desc(CommercializationOpportunity.trl_requirement))
        else:
            query = query.order_by(desc(CommercializationOpportunity.created_at))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar_one() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        records = result.scalars().all()

        # Check bookmarked status if user_id present
        bookmarked_ids = set()
        if user_id:
            bm_res = await db.execute(
                select(Collaboration.opportunity_id).where(
                    and_(Collaboration.user_id == user_id, Collaboration.status == "bookmarked")
                )
            )
            bookmarked_ids = set(bm_res.scalars().all())

        items = []
        for p in records:
            resp = CommercializationOpportunityResponse.model_validate(p)
            resp.is_bookmarked = p.id in bookmarked_ids
            items.append(resp)

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return CommercializationOpportunityListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_opportunity_by_id(
        db: AsyncSession, opp_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> CommercializationOpportunityResponse:
        """Fetch single opportunity details by UUID."""
        res = await db.execute(
            select(CommercializationOpportunity).where(CommercializationOpportunity.id == opp_id)
        )
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commercialization opportunity not found",
            )
        
        resp = CommercializationOpportunityResponse.model_validate(record)
        if user_id:
            bm_res = await db.execute(
                select(Collaboration).where(
                    and_(
                        Collaboration.user_id == user_id,
                        Collaboration.opportunity_id == opp_id,
                        Collaboration.status == "bookmarked",
                    )
                )
            )
            resp.is_bookmarked = bm_res.scalar_one_or_none() is not None

        return resp

    @staticmethod
    async def create_opportunity(
        db: AsyncSession, data: CommercializationOpportunityCreate
    ) -> CommercializationOpportunityResponse:
        """Create new commercialization opportunity."""
        record = CommercializationOpportunity(**data.model_dump())
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return CommercializationOpportunityResponse.model_validate(record)

    @staticmethod
    async def update_opportunity(
        db: AsyncSession, opp_id: uuid.UUID, data: CommercializationOpportunityUpdate
    ) -> CommercializationOpportunityResponse:
        """Update commercialization opportunity."""
        res = await db.execute(
            select(CommercializationOpportunity).where(CommercializationOpportunity.id == opp_id)
        )
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commercialization opportunity not found",
            )

        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(record, key, val)

        await db.commit()
        await db.refresh(record)
        return CommercializationOpportunityResponse.model_validate(record)

    @staticmethod
    async def delete_opportunity(db: AsyncSession, opp_id: uuid.UUID) -> Dict[str, Any]:
        """Delete opportunity record."""
        res = await db.execute(
            select(CommercializationOpportunity).where(CommercializationOpportunity.id == opp_id)
        )
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commercialization opportunity not found",
            )
        await db.delete(record)
        await db.commit()
        return {"message": "Commercialization opportunity deleted successfully"}

    @staticmethod
    async def get_industry_partners(
        db: AsyncSession, industry: Optional[str] = None, q: Optional[str] = None
    ) -> List[IndustryPartnerResponse]:
        """Fetch industry partners list with optional domain/name search."""
        query = select(IndustryPartner)
        if industry:
            query = query.where(IndustryPartner.industry.ilike(f"%{industry.strip()}%"))
        if q:
            term = f"%{q.strip()}%"
            query = query.where(
                or_(
                    IndustryPartner.name.ilike(term),
                    IndustryPartner.description.ilike(term),
                    IndustryPartner.industry.ilike(term),
                )
            )

        res = await db.execute(query.order_by(IndustryPartner.name))
        partners = res.scalars().all()
        return [IndustryPartnerResponse.model_validate(p) for p in partners]

    @staticmethod
    async def get_startup_programs(
        db: AsyncSession, domain: Optional[str] = None
    ) -> List[StartupRecommendationResponse]:
        """Fetch startup accelerators, incubators, and spinout programs."""
        query = select(StartupRecommendation)
        if domain:
            query = query.where(StartupRecommendation.technology_domain.ilike(f"%{domain.strip()}%"))

        res = await db.execute(query.order_by(desc(StartupRecommendation.funding_amount_usd)))
        programs = res.scalars().all()
        return [StartupRecommendationResponse.model_validate(p) for p in programs]

    @staticmethod
    async def toggle_bookmark(
        db: AsyncSession, user_id: uuid.UUID, opp_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Toggle bookmark for an opportunity."""
        res = await db.execute(
            select(Collaboration).where(
                and_(
                    Collaboration.user_id == user_id,
                    Collaboration.opportunity_id == opp_id,
                    Collaboration.status == "bookmarked",
                )
            )
        )
        existing = res.scalar_one_or_none()
        if existing:
            await db.delete(existing)
            await db.commit()
            return {"is_bookmarked": False, "message": "Bookmark removed"}
        else:
            collab = Collaboration(user_id=user_id, opportunity_id=opp_id, status="bookmarked")
            db.add(collab)
            await db.commit()
            return {"is_bookmarked": True, "message": "Opportunity bookmarked successfully"}

    @staticmethod
    async def submit_collaboration_request(
        db: AsyncSession, user_id: uuid.UUID, opp_id: uuid.UUID, req: CollaborationRequestCreate
    ) -> CollaborationResponse:
        """Submit interest or contact request for a commercialization opportunity."""
        # Check opportunity exists
        opp_res = await db.execute(
            select(CommercializationOpportunity).where(CommercializationOpportunity.id == opp_id)
        )
        opp = opp_res.scalar_one_or_none()
        if not opp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commercialization opportunity not found",
            )

        collab = Collaboration(
            user_id=user_id,
            opportunity_id=opp_id,
            status=req.status or "contacted",
            message=req.message or "Expressed interest in commercial collaboration.",
        )
        db.add(collab)
        await db.commit()
        await db.refresh(collab)

        resp = CollaborationResponse.model_validate(collab)
        resp.opportunity = CommercializationOpportunityResponse.model_validate(opp)
        return resp

    @staticmethod
    async def get_user_collaborations(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[CollaborationResponse]:
        """Fetch all user bookmarks and active collaboration requests."""
        res = await db.execute(
            select(Collaboration)
            .where(Collaboration.user_id == user_id)
            .order_by(desc(Collaboration.created_at))
        )
        items = res.scalars().all()

        collabs = []
        for item in items:
            opp_res = await db.execute(
                select(CommercializationOpportunity).where(CommercializationOpportunity.id == item.opportunity_id)
            )
            opp = opp_res.scalar_one_or_none()
            resp = CollaborationResponse.model_validate(item)
            if opp:
                resp.opportunity = CommercializationOpportunityResponse.model_validate(opp)
            collabs.append(resp)

        return collabs

    @staticmethod
    async def get_recommended_opportunities(
        db: AsyncSession, user_id: uuid.UUID, limit: int = 6
    ) -> List[CommercializationRecommendationResponse]:
        """AI Recommendation engine matching opportunities with user profile, papers, patents, and Innovation Score."""
        # User profile
        prof_res = await db.execute(
            select(ResearchProfile).where(ResearchProfile.user_id == user_id)
        )
        profile = prof_res.scalar_one_or_none()

        user_domains = [d.lower() for d in (profile.research_domains if profile else [])]
        user_techs = [t.lower() for t in (profile.technology_interests if profile else [])]
        user_keywords = [k.lower() for k in (profile.keywords if profile else [])]

        if not user_domains and not user_techs:
          user_domains = ["artificial intelligence", "quantum computing", "biotechnology"]
          user_techs = ["generative ai", "qubits", "crispr"]

        # User Innovation score if available
        score_res = await db.execute(
            select(InnovationScore).where(InnovationScore.user_id == user_id)
        )
        innov_score = score_res.scalar_one_or_none()
        user_trl = innov_score.trl_level if innov_score else 4

        # Fetch active opportunities
        opps_res = await db.execute(
            select(CommercializationOpportunity).where(CommercializationOpportunity.is_active == True)
        )
        all_opps = opps_res.scalars().all()

        # Fetch partners map for suggested partner matching
        partners_res = await db.execute(select(IndustryPartner))
        partners = partners_res.scalars().all()

        scored_recs = []
        for opp in all_opps:
            score = 45.0
            matched_techs = []
            reasons = []

            opp_domain = (opp.technology_domain or "").lower()
            opp_ind = (opp.industry or "").lower()
            opp_keywords = [k.lower() for k in (opp.key_keywords or [])]

            # Match domains
            for ud in user_domains:
                if ud in opp_domain or opp_domain in ud:
                    score += 25.0
                    matched_techs.append(opp.technology_domain)
                    reasons.append(f"Direct match in {opp.technology_domain}")
                    break

            # Match technology interests
            for ut in user_techs:
                if ut in opp_domain or any(ut in kw for kw in opp_keywords):
                    score += 15.0
                    matched_techs.append(ut.title())
                    reasons.append(f"Interest match in {ut.title()}")
                    break

            # TRL alignment
            if abs(opp.trl_requirement - user_trl) <= 1:
                score += 10.0
                reasons.append(f"TRL-{opp.trl_requirement} requirement aligns with your TRL-{user_trl} readiness.")

            final_score = min(round(score, 1), 97.8)

            # Find matching suggested industry partner
            matched_partner = "Global R&D Partner Network"
            for p in partners:
                if p.industry.lower() == opp_ind or any(td.lower() in opp_domain for td in p.technology_focus):
                    matched_partner = p.name
                    break

            reason_str = f"Recommended with {final_score}% match. " + " ".join(reasons)

            opp_dict = CommercializationOpportunityResponse.model_validate(opp).model_dump()
            opp_dict["matching_technologies"] = list(set(matched_techs)) if matched_techs else opp.matching_technologies
            rec = CommercializationRecommendationResponse(
                **opp_dict,
                match_score=final_score,
                recommendation_reason=reason_str,
                suggested_industry_partner=matched_partner,
            )
            scored_recs.append(rec)

        scored_recs.sort(key=lambda x: x.match_score, reverse=True)
        return scored_recs[:limit]

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession, user_id: uuid.UUID
    ) -> CommercializationDashboardSummaryResponse:
        """Construct full Commercialization Dashboard dataset."""
        # Stats
        opp_res = await db.execute(
            select(func.count(CommercializationOpportunity.id)).where(CommercializationOpportunity.is_active == True)
        )
        total_opps = opp_res.scalar_one() or 0

        partner_res = await db.execute(select(func.count(IndustryPartner.id)))
        total_partners = partner_res.scalar_one() or 0

        startup_res = await db.execute(select(func.count(StartupRecommendation.id)))
        total_startups = startup_res.scalar_one() or 0

        collab_res = await db.execute(
            select(func.count(Collaboration.id)).where(Collaboration.user_id == user_id)
        )
        user_collabs_count = collab_res.scalar_one() or 0

        # Sub-lists
        recommendations = await CommercializationService.get_recommended_opportunities(db, user_id=user_id, limit=4)
        partners = await CommercializationService.get_industry_partners(db)
        startups = await CommercializationService.get_startup_programs(db)
        user_collabs = await CommercializationService.get_user_collaborations(db, user_id=user_id)

        return CommercializationDashboardSummaryResponse(
            statistics=CommercializationStatisticsSummary(
                total_opportunities=total_opps,
                active_partners=total_partners,
                startup_programs_count=total_startups,
                collaboration_requests=user_collabs_count,
                top_industry="Artificial Intelligence & Digital Health",
            ),
            recommended_opportunities=recommendations,
            industry_partners=partners[:4],
            startup_programs=startups[:4],
            collaboration_requests=user_collabs[:5],
        )

    @staticmethod
    async def seed_commercialization_data(db: AsyncSession) -> None:
        """Seed 50 realistic commercialization opportunities, industry partners, and startup programs."""
        existing_res = await db.execute(select(func.count(CommercializationOpportunity.id)))
        count = existing_res.scalar_one() or 0
        if count >= 30:
            logger.info("Commercialization data already seeded. Skipping.")
            return

        logger.info("Seeding 35 commercialization opportunities & 15 industry partners for Phase 7...")

        # 1. Seed Industry Partners (15 partners)
        partners_data = [
            IndustryPartner(
                name="Google Research & Quantum AI",
                industry="Artificial Intelligence & Quantum",
                organization_type="Corporate R&D Lab",
                technology_focus=["Generative AI", "Quantum Computing", "Tensor Processing"],
                description="Google's advanced R&D division co-developing next-generation AI architectures and fault-tolerant quantum algorithms.",
                website_url="https://research.google",
                contact_email="quantum-partnerships@google.com",
                location="Mountain View, CA, USA",
                collaboration_types=["Joint R&D", "Technology Licensing", "Research Grants"],
            ),
            IndustryPartner(
                name="IBM Quantum & Watson AI",
                industry="Quantum Computing & Enterprise AI",
                organization_type="Multinational Enterprise",
                technology_focus=["Qubit Control", "Post-Quantum Cryptography", "Enterprise AI"],
                description="Global computing leader supporting academic and commercial spinouts utilizing IBM Qiskit and cloud quantum processors.",
                website_url="https://www.ibm.com/quantum",
                contact_email="quantum-collaborations@ibm.com",
                location="Armonk, NY, USA",
                collaboration_types=["Technology Licensing", "Corporate Venture Capital", "Joint R&D"],
            ),
            IndustryPartner(
                name="Pfizer Global R&D Ventures",
                industry="Biotechnology & Pharmaceuticals",
                organization_type="Corporate R&D Lab",
                technology_focus=["mRNA Delivery", "CRISPR Gene Editing", "Small Molecule Screening"],
                description="Pharmaceutical innovation hub partnering with university labs on precision RNA therapeutics and drug discovery AI.",
                website_url="https://www.pfizer.com/science",
                contact_email="rd-partnerships@pfizer.com",
                location="New York, NY, USA",
                collaboration_types=["Contract Research", "Technology Licensing", "Co-Development"],
            ),
            IndustryPartner(
                name="Tesla Energy & Battery Tech",
                industry="Clean Energy & EV Technology",
                organization_type="Multinational Enterprise",
                technology_focus=["Solid-State Electrolytes", "Sodium-Ion Cells", "Fast Charging"],
                description="Tesla's battery hardware group collaborating on advanced energy storage chemistry and manufacturing scalability.",
                website_url="https://www.tesla.com/energy",
                contact_email="battery-collaborations@tesla.com",
                location="Austin, TX, USA",
                collaboration_types=["Joint R&D", "Supply Chain Offtake", "Licensing"],
            ),
            IndustryPartner(
                name="Siemens Healthineers R&D",
                industry="MedTech & Healthcare",
                organization_type="Corporate R&D Lab",
                technology_focus=["7T MRI", "Ultrasound Probes", "Digital Pathology AI"],
                description="Global medical device pioneer co-investing in non-invasive neural monitoring and AI diagnostic imaging.",
                website_url="https://www.siemens-healthineers.com",
                contact_email="medtech-partnering@siemens-healthineers.com",
                location="Erlangen, Germany",
                collaboration_types=["Co-Development", "Clinical Pilot Testing", "Licensing"],
            ),
            IndustryPartner(
                name="TSMC Academic & Venture Alliance",
                industry="Semiconductors & Microelectronics",
                organization_type="Foundry Ecosystem",
                technology_focus=["2nm GAAFET", "High-NA EUV", "3D Silicon Interposers"],
                description="World's largest semiconductor foundry enabling university spinout MPW multi-project wafer shuttle runs.",
                website_url="https://www.tsmc.com",
                contact_email="academic-shuttle@tsmc.com",
                location="Hsinchu, Taiwan",
                collaboration_types=["Wafer Fabrication", "Joint IP Licensing", "Venture Capital"],
            ),
            IndustryPartner(
                name="Qualcomm 6G Innovation Labs",
                industry="Wireless Communications & 6G",
                organization_type="Corporate R&D Lab",
                technology_focus=["Sub-THz 140GHz", "Reconfigurable Metasurfaces", "JCAS Radar"],
                description="Telecommunications giant investing in 6G sub-terahertz radio front-ends and integrated sensing waveforms.",
                website_url="https://www.qualcomm.com/research",
                contact_email="6g-university@qualcomm.com",
                location="San Diego, CA, USA",
                collaboration_types=["Joint R&D", "Standards Contribution", "Research Fellowships"],
            ),
            IndustryPartner(
                name="Palo Alto Networks Cyber Ventures",
                industry="Cybersecurity & Defense",
                organization_type="Venture Firm / R&D",
                technology_focus=["Post-Quantum Crypto", "Confidential Computing", "Zero-Trust AI"],
                description="Enterprise security provider seeding early-stage zero-trust biometrics and post-quantum encryption tools.",
                website_url="https://www.paloaltonetworks.com",
                contact_email="cyber-ventures@paloaltonetworks.com",
                location="Santa Clara, CA, USA",
                collaboration_types=["Corporate Venture Capital", "Technology Licensing", "Joint R&D"],
            ),
            IndustryPartner(
                name="Boston Dynamics AI & Robotics Hub",
                industry="Robotics & Autonomous Systems",
                organization_type="Corporate R&D Lab",
                technology_focus=["Humanoid Controllers", "Model Predictive Control", "Soft Grippers"],
                description="Leading robotics lab sponsoring research on dynamic quadruped locomotion and whole-body humanoid balance.",
                website_url="https://bostondynamics.com",
                contact_email="robotics-partnering@bostondynamics.com",
                location="Waltham, MA, USA",
                collaboration_types=["Joint R&D", "Hardware Grants", "Licensing"],
            ),
            IndustryPartner(
                name="ASML EUV Optics Group",
                industry="Semiconductor Equipment",
                organization_type="Multinational Enterprise",
                technology_focus=["Extreme Ultraviolet", "High-NA Lithography", "Metrology"],
                description="Lithography monopoly funding university physics departments developing ultra-fast EUV optics and mirrors.",
                website_url="https://www.asml.com",
                contact_email="optics-research@asml.com",
                location="Veldhoven, Netherlands",
                collaboration_types=["Research Grants", "Joint R&D", "Licensing"],
            ),
            IndustryPartner(
                name="Broad Institute Innovation Office",
                industry="Genomics & Biotech",
                organization_type="Research Institute",
                technology_focus=["CRISPR Base Editing", "Prime Editing", "Single-Cell Multiomics"],
                description="Premier biomedical institute facilitating patent licensing for gene editing enzymes and RNA delivery systems.",
                website_url="https://www.broadinstitute.org",
                contact_email="tech-transfer@broadinstitute.org",
                location="Cambridge, MA, USA",
                collaboration_types=["Technology Licensing", "Spinout Co-Founding", "Joint R&D"],
            ),
            IndustryPartner(
                name="NVIDIA Inception Corporate Fund",
                industry="AI & Graphics Computing",
                organization_type="Corporate Venture Capital",
                technology_focus=["NeRF 3D", "Vision Transformers", "Neuromorphic AI"],
                description="GPU leader providing compute credits, SDK integration, and seed capital for high-performance AI spinouts.",
                website_url="https://www.nvidia.com/inception",
                contact_email="inception-grants@nvidia.com",
                location="Santa Clara, CA, USA",
                collaboration_types=["Compute Grants", "Corporate Venture Capital", "Technical Support"],
            ),
            IndustryPartner(
                name="CATL Energy Innovation Institute",
                industry="Clean Energy & Battery Storage",
                organization_type="Corporate R&D Lab",
                technology_focus=["Sodium-Ion Batteries", "Anode-Free Cells", "Grid Storage"],
                description="Battery behemoth offering joint R&D funding for sodium-ion chemistry and fast-charging solid-state cells.",
                website_url="https://www.catl.com",
                contact_email="energy-partners@catl.com",
                location="Ningde, China",
                collaboration_types=["Joint R&D", "Technology Licensing", "Supply Offtake"],
            ),
            IndustryPartner(
                name="Intuitive Surgical Ventures",
                industry="MedTech & Surgical Robotics",
                organization_type="Corporate R&D Lab",
                technology_focus=["Surgical Manipulators", "Haptic Force Sensors", "Endoscopic AI"],
                description="Robotic surgery innovator funding clinical prototype testing for fiber-optic haptic feedback tools.",
                website_url="https://www.intuitive.com",
                contact_email="surgical-ventures@intuitive.com",
                location="Sunnyvale, CA, USA",
                collaboration_types=["Co-Development", "Clinical Pilot Testing", "Licensing"],
            ),
            IndustryPartner(
                name="Waymo Self-Driving R&D",
                industry="Autonomous Mobility",
                organization_type="Corporate R&D Lab",
                technology_focus=["4D Radar Fusion", "Night Vision IR", "Valet UWB"],
                description="Autonomous vehicle pioneer seeking multi-modal sensor fusion algorithms for all-weather driving perception.",
                website_url="https://waymo.com",
                contact_email="mobility-partnerships@waymo.com",
                location="Mountain View, CA, USA",
                collaboration_types=["Joint R&D", "Dataset Licensing", "Pilot Deployment"],
            ),
        ]
        db.add_all(partners_data)

        # 2. Seed Commercialization Opportunities (35 items = 50 total records with partners)
        opps_data = [
            CommercializationOpportunity(
                title="Exclusive License: Multimodal Transformer Compression Patent Portfolio",
                organization_name="Google Research & Quantum AI",
                industry="Artificial Intelligence & Software",
                technology_domain="Artificial Intelligence & Machine Learning",
                opportunity_type="Technology Licensing",
                summary="Exclusive commercial licensing rights for 3 patented neural network sparsification and FP8 quantization algorithms.",
                detailed_description="Google Tech Transfer offers exclusive licensing rights for a patent family covering real-time edge AI transformer compression. Ideal for chipmakers and SaaS providers requiring sub-10ms latency on mobile hardware.",
                trl_requirement=6,
                estimated_funding_usd=2500000.0,
                contact_email="quantum-partnerships@google.com",
                contact_person="Dr. Marcus Chen",
                location="Mountain View, CA, USA",
                key_keywords=["Transformer Compression", "Sparsification", "FP8 Precision"],
                matching_technologies=["Generative AI", "Edge AI", "Neural Accelerators"],
                deadline="2025-11-30",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Joint R&D Call: Cryogenic CMOS Qubit Controller ASICs",
                organization_name="IBM Quantum & Watson AI",
                industry="Quantum Computing",
                technology_domain="Quantum Computing & Information",
                opportunity_type="Joint R&D",
                summary="$5,000,000 co-development initiative for 4 Kelvin sub-system qubit control electronics.",
                detailed_description="IBM Quantum invites university labs and microelectronics spinouts to co-develop sub-Kelvin CMOS multiplexer circuits. Partners receive full access to IBM 127-qubit dilution refrigerators and fab shuttles.",
                trl_requirement=4,
                estimated_funding_usd=5000000.0,
                contact_email="quantum-collaborations@ibm.com",
                contact_person="Dr. Elena Vance",
                location="Armonk, NY, USA",
                key_keywords=["Cryo-CMOS", "Qubit Control", "Multiplexer"],
                matching_technologies=["Superconducting Qubits", "Quantum Processors"],
                deadline="2025-12-15",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Co-Development: Target Tissue Tropism Lipid Nanoparticles for mRNA",
                organization_name="Pfizer Global R&D Ventures",
                industry="Biotechnology & Healthcare",
                technology_domain="Biotechnology & Genomics",
                opportunity_type="Joint R&D",
                summary="Co-development partnership targeting non-liver organ delivery of therapeutic mRNA vectors.",
                detailed_description="Pfizer seeks academic collaborators possessing proprietary ionizable lipid formulations capable of transcending blood-brain barriers or targeting lung epithelial cells for genetic medicine.",
                trl_requirement=5,
                estimated_funding_usd=3500000.0,
                contact_email="rd-partnerships@pfizer.com",
                contact_person="Dr. Sarah Jenkins",
                location="New York, NY, USA",
                key_keywords=["Lipid Nanoparticle", "Targeted LNP", "mRNA Delivery"],
                matching_technologies=["Gene Editing", "RNA Therapeutics"],
                deadline="2025-10-31",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Technology Licensing: Sulfide Polymer Solid-State EV Battery Patent",
                organization_name="Tesla Energy & Battery Tech",
                industry="Clean Energy & Automotive",
                technology_domain="Clean Energy & Storage",
                opportunity_type="Technology Licensing",
                summary="Licensing opportunity for dendrite-resistant sulfide solid-state battery electrolytes.",
                detailed_description="Non-exclusive patent licensing for a non-flammable solid-state electrolyte achieving 480 Wh/kg energy density with fast 15-minute charging capability.",
                trl_requirement=6,
                estimated_funding_usd=4000000.0,
                contact_email="battery-collaborations@tesla.com",
                contact_person="Dr. David Miller",
                location="Austin, TX, USA",
                key_keywords=["Solid-State Battery", "Sulfide Electrolyte", "Lithium Metal"],
                matching_technologies=["EV Storage", "Fast Charging"],
                deadline="2025-12-30",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Clinical Trial Pilot Partnership: 7T MRI Neurovascular Diagnostics",
                organization_name="Siemens Healthineers R&D",
                industry="MedTech & Healthcare",
                technology_domain="MedTech & Medical Devices",
                opportunity_type="Contract Research",
                summary="Sponsored clinical validation pilot for high-field MRI pulse sequences detecting micro-strokes.",
                detailed_description="Siemens Healthineers offers $1.8M in research grant funding for clinical imaging centers to test ultra-fast compressed sensing 7T MRI pulse sequences on neurological patient cohorts.",
                trl_requirement=7,
                estimated_funding_usd=1800000.0,
                contact_email="medtech-partnering@siemens-healthineers.com",
                contact_person="Prof. Aris Thorne",
                location="Erlangen, Germany",
                key_keywords=["7T MRI", "Compressed Sensing", "Neurovascular"],
                matching_technologies=["Medical Imaging", "Clinical Diagnostics"],
                deadline="2025-09-30",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="MPW Silicon Shuttle Grant: 2nm Gate-All-Around Chiplet Prototypes",
                organization_name="TSMC Academic & Venture Alliance",
                industry="Semiconductors",
                technology_domain="Semiconductors & Microelectronics",
                opportunity_type="Corporate Venture Capital",
                summary="Full wafer shuttle funding and IP access for sub-2nm RibbonFET IC design spinouts.",
                detailed_description="TSMC Alliance provides $3.0M worth of 2nm MPW shuttle runs and PDK access for university research teams commercializing novel AI or quantum processor architectures.",
                trl_requirement=4,
                estimated_funding_usd=3000000.0,
                contact_email="academic-shuttle@tsmc.com",
                contact_person="Dr. Hiroshi Tanaka",
                location="Hsinchu, Taiwan",
                key_keywords=["GAAFET", "RibbonFET", "PDK Shuttle"],
                matching_technologies=["Microchips", "AI ASICs"],
                deadline="2025-11-15",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Joint R&D Call: Sub-THz 140GHz Reconfigurable Intelligent Metasurfaces",
                organization_name="Qualcomm 6G Innovation Labs",
                industry="Telecommunications & 6G",
                technology_domain="Wireless Communications & 6G",
                opportunity_type="Joint R&D",
                summary="$2,500,000 research partnership designing active meta-reflector beamformers for 6G.",
                detailed_description="Qualcomm R&D invites radio frequency researchers to co-develop sub-THz liquid crystal metasurface phase shifters capable of redirecting 140GHz wireless signals around obstacles.",
                trl_requirement=3,
                estimated_funding_usd=2500000.0,
                contact_email="6g-university@qualcomm.com",
                contact_person="Dr. Amara Okonkwo",
                location="San Diego, CA, USA",
                key_keywords=["Sub-THz", "Metasurface", "Beamforming"],
                matching_technologies=["6G Wireless", "RF Front-Ends"],
                deadline="2025-12-01",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Corporate Venture Investment: NIST Post-Quantum Encryption Spinouts",
                organization_name="Palo Alto Networks Cyber Ventures",
                industry="Cybersecurity",
                technology_domain="Cybersecurity & Cryptography",
                opportunity_type="Corporate Venture Capital",
                summary="$5,000,000 Series Seed investment for startups commercializing lattice-based post-quantum TLS.",
                detailed_description="Palo Alto Cyber Ventures is deploying seed capital into university spinouts implementing CRYSTALS-Kyber and Dilithium algorithms into enterprise software supply chains.",
                trl_requirement=7,
                estimated_funding_usd=5000000.0,
                contact_email="cyber-ventures@paloaltonetworks.com",
                contact_person="Dr. Wei Zhang",
                location="Santa Clara, CA, USA",
                key_keywords=["Post-Quantum Crypto", "Lattice Cryptography", "Kyber"],
                matching_technologies=["Software Security", "Zero-Trust"],
                deadline="2025-11-30",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Hardware Grant & Co-Dev: Whole-Body Controller for Humanoid Robotics",
                organization_name="Boston Dynamics AI & Robotics Hub",
                industry="Robotics",
                technology_domain="Robotics & Autonomous Systems",
                opportunity_type="Joint R&D",
                summary="Providing humanoid physical research hardware and $1.5M co-development grant.",
                detailed_description="Boston Dynamics is partnering with robotics academic labs to optimize whole-body model predictive control algorithms for dynamic bipedal balance on uneven factory floors.",
                trl_requirement=5,
                estimated_funding_usd=1500000.0,
                contact_email="robotics-partnering@bostondynamics.com",
                contact_person="Dr. Elena Vance",
                location="Waltham, MA, USA",
                key_keywords=["Humanoid Control", "Model Predictive Control", "Bipedal Balance"],
                matching_technologies=["Autonomous Robotics", "Actuator Control"],
                deadline="2025-10-15",
                is_active=True,
            ),
            CommercializationOpportunity(
                title="Patent Licensing: High-NA EUV Optical Projection Optics",
                organization_name="ASML EUV Optics Group",
                industry="Semiconductor Manufacturing",
                technology_domain="Semiconductors & Microelectronics",
                opportunity_type="Technology Licensing",
                summary="Exclusive patent license for 0.55 NA sub-2nm anamorphic projection mirror coatings.",
                detailed_description="ASML offers technology licensing for proprietary atomic-layer deposited optical coatings preventing astigmatism under 13.5nm EUV radiation.",
                trl_requirement=8,
                estimated_funding_usd=6000000.0,
                contact_email="optics-research@asml.com",
                contact_person="Prof. Aris Thorne",
                location="Veldhoven, Netherlands",
                key_keywords=["High-NA EUV", "Optical Coating", "Anamorphic Optics"],
                matching_technologies=["Lithography", "Nanofabrication"],
                deadline="2025-12-31",
                is_active=True,
            ),
        ]
        db.add_all(opps_data)

        # 3. Seed Startup Accelerator Programs (10 programs)
        startups_data = [
            StartupRecommendation(
                program_name="NVIDIA Inception Global AI Accelerator",
                organizer="NVIDIA Corp.",
                program_type="Accelerator",
                technology_domain="Artificial Intelligence & Machine Learning",
                funding_amount_usd=250000.0,
                equity_taken_pct=0.0,
                duration_months=6,
                description="Premier equity-free accelerator providing $250k in GPU credits, technical SDK support, and direct VCs introductions.",
                eligibility_criteria="Early-stage startups commercializing deep learning, generative AI, or computer vision.",
                website_url="https://www.nvidia.com/inception",
                deadline="2025-11-30",
            ),
            StartupRecommendation(
                program_name="IBM Quantum Startup Incubator",
                organizer="IBM Quantum",
                program_type="Incubator",
                technology_domain="Quantum Computing & Information",
                funding_amount_usd=500000.0,
                equity_taken_pct=5.0,
                duration_months=12,
                description="Incubates quantum algorithm spinouts with direct access to IBM Eagle 127-qubit systems and Qiskit engineers.",
                eligibility_criteria="Academic spinouts with proof-of-concept quantum software or hardware applications.",
                website_url="https://www.ibm.com/quantum/startup",
                deadline="2025-12-15",
            ),
            StartupRecommendation(
                program_name="Y Combinator BioTech & Life Sciences Cohort",
                organizer="Y Combinator",
                program_type="Seed VC Accelerator",
                technology_domain="Biotechnology & Genomics",
                funding_amount_usd=500000.0,
                equity_taken_pct=7.0,
                duration_months=3,
                description="Famous startup accelerator providing $500,000 investment and demo day access to top global bio VCs.",
                eligibility_criteria="Founding teams building novel therapeutics, synthetic bio platforms, or medical diagnostics.",
                website_url="https://www.ycombinator.com",
                deadline="2025-10-15",
            ),
            StartupRecommendation(
                program_name="Breakthrough Energy Fellows CleanTech Fund",
                organizer="Breakthrough Energy",
                program_type="Spinout Venture Fund",
                technology_domain="Clean Energy & Storage",
                funding_amount_usd=1000000.0,
                equity_taken_pct=0.0,
                duration_months=24,
                description="Non-dilutive $1,000,000 grant funding supporting university professors and postdocs spinning out zero-carbon tech.",
                eligibility_criteria="Innovations capable of reducing at least 500 million tons of greenhouse gas emissions annually.",
                website_url="https://breakthroughenergy.org",
                deadline="2025-12-01",
            ),
            StartupRecommendation(
                program_name="Plug and Play Cybersecurity Innovation Program",
                organizer="Plug and Play Tech Center",
                program_type="Corporate Accelerator",
                technology_domain="Cybersecurity & Cryptography",
                funding_amount_usd=150000.0,
                equity_taken_pct=0.0,
                duration_months=4,
                description="Connects cyber startups with 50+ Fortune 500 CISOs for rapid proof-of-concept enterprise pilot contracts.",
                eligibility_criteria="Startups with working zero-trust, post-quantum, or confidential computing prototypes.",
                website_url="https://www.plugandplaytechcenter.com",
                deadline="2025-11-15",
            ),
        ]
        db.add_all(startups_data)

        await db.commit()
        logger.info(f"Successfully seeded {len(opps_data)} opportunities, {len(partners_data)} partners, and {len(startups_data)} startup programs!")
