"""
Service layer for Technology Intelligence, Innovation Scoring, Opportunity Analysis, and Seeding.
"""
import logging
import math
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.technology import TechnologyTrend, InnovationScore
from app.models.research_profile import ResearchProfile, Publication, Patent
from app.models.patent import PatentRecord
from app.schemas.technology import (
    TechnologyTrendResponse,
    TechnologyTrendListResponse,
    InnovationScoreResponse,
    InnovationScoreBreakdown,
    OpportunityAnalysisItem,
    OpportunityAnalysisResponse,
    TechnologyDashboardSummaryResponse,
    TechnologyStatisticsSummary,
)

logger = logging.getLogger(__name__)


class TechnologyService:
    @staticmethod
    async def search_technology_trends(
        db: AsyncSession,
        q: Optional[str] = None,
        domain: Optional[str] = None,
        maturity_level: Optional[str] = None,
        sort_by: str = "growth_desc",
        page: int = 1,
        page_size: int = 12,
    ) -> TechnologyTrendListResponse:
        """Search technology trends with keyword, domain, maturity level filters, sorting, and pagination."""
        query = select(TechnologyTrend)

        filters = []
        if q:
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    TechnologyTrend.name.ilike(term),
                    TechnologyTrend.summary.ilike(term),
                    TechnologyTrend.technology_domain.ilike(term),
                    TechnologyTrend.opportunity_description.ilike(term),
                )
            )
        if domain:
            filters.append(TechnologyTrend.technology_domain.ilike(f"%{domain.strip()}%"))
        if maturity_level:
            filters.append(TechnologyTrend.maturity_level.ilike(f"%{maturity_level.strip()}%"))

        if filters:
            query = query.where(and_(*filters))

        # Sorting
        if sort_by == "growth_desc":
            query = query.order_by(desc(TechnologyTrend.growth_rate))
        elif sort_by == "market_desc":
            query = query.order_by(desc(TechnologyTrend.market_size_usd_b))
        elif sort_by == "trl_desc":
            query = query.order_by(desc(TechnologyTrend.trl_level))
        elif sort_by == "trl_asc":
            query = query.order_by(asc(TechnologyTrend.trl_level))
        else:
            query = query.order_by(desc(TechnologyTrend.created_at))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar_one() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await db.execute(query)
        records = result.scalars().all()

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        items = [TechnologyTrendResponse.model_validate(t) for t in records]
        return TechnologyTrendListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_emerging_technologies(
        db: AsyncSession, limit: int = 6
    ) -> List[TechnologyTrendResponse]:
        """Fetch top emerging technology trends."""
        res = await db.execute(
            select(TechnologyTrend)
            .where(TechnologyTrend.is_emerging == True)
            .order_by(desc(TechnologyTrend.growth_rate))
            .limit(limit)
        )
        trends = res.scalars().all()
        return [TechnologyTrendResponse.model_validate(t) for t in trends]

    @staticmethod
    async def get_trend_by_id(db: AsyncSession, trend_id: uuid.UUID) -> TechnologyTrendResponse:
        """Fetch single technology trend detail."""
        res = await db.execute(select(TechnologyTrend).where(TechnologyTrend.id == trend_id))
        trend = res.scalar_one_or_none()
        if not trend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technology trend not found",
            )
        return TechnologyTrendResponse.model_validate(trend)

    @staticmethod
    async def calculate_user_innovation_score(
        db: AsyncSession, user_id: uuid.UUID
    ) -> InnovationScoreResponse:
        """Compute or retrieve Innovation Score based on user's Research Profile, Publications, and Patents."""
        # Check existing score in DB
        score_res = await db.execute(
            select(InnovationScore).where(InnovationScore.user_id == user_id)
        )
        existing_score = score_res.scalar_one_or_none()

        # Fetch profile
        prof_res = await db.execute(
            select(ResearchProfile).where(ResearchProfile.user_id == user_id)
        )
        profile = prof_res.scalar_one_or_none()

        # Fetch publications count & total citations
        pubs_count = 0
        total_citations = 0
        h_index = 0
        if profile:
            h_index = profile.h_index or 0
            total_citations = profile.total_citations or 0
            pub_res = await db.execute(
                select(func.count(Publication.id)).where(Publication.profile_id == profile.id)
            )
            pubs_count = pub_res.scalar_one() or 0

        # Fetch patents count & granted patents count
        patents_count = 0
        granted_patents_count = 0
        if profile:
            pat_res = await db.execute(
                select(func.count(Patent.id)).where(Patent.profile_id == profile.id)
            )
            patents_count = pat_res.scalar_one() or 0
            
            granted_res = await db.execute(
                select(func.count(Patent.id)).where(
                    and_(Patent.profile_id == profile.id, Patent.status == "granted")
                )
            )
            granted_patents_count = granted_res.scalar_one() or 0

        # Also check global patent records attributed by email/name if any
        global_pat_res = await db.execute(select(func.count(PatentRecord.id)))
        global_patents_total = global_pat_res.scalar_one() or 0

        # Compute Sub-Scores:
        # 1. Research Strength (0-100)
        res_score = min(
            (pubs_count * 5.0) + (h_index * 4.0) + (min(total_citations, 500) / 10.0) + 40.0,
            96.0,
        )

        # 2. Patent Strength (0-100)
        pat_score = min(
            (patents_count * 15.0) + (granted_patents_count * 20.0) + 35.0,
            95.0,
        )

        # 3. Commercial Potential (0-100)
        user_domains = profile.research_domains if profile else ["AI", "Quantum"]
        user_techs = profile.technology_interests if profile else ["Generative AI"]
        comm_score = min(
            45.0 + (len(user_domains) * 8.0) + (len(user_techs) * 7.0) + (granted_patents_count * 10.0),
            98.0,
        )

        # 4. Overall Innovation Score (0-100)
        overall = round((res_score * 0.35) + (pat_score * 0.35) + (comm_score * 0.30), 1)

        # 5. Technology Readiness Level (TRL 1 to 9)
        if granted_patents_count >= 2:
            trl = 7  # System Prototype / Commercial Demonstration
        elif patents_count >= 1 or granted_patents_count == 1:
            trl = 5  # Technology Validated in Relevant Environment
        elif pubs_count >= 3:
            trl = 4  # Component Validation in Lab
        else:
            trl = 3  # Analytical & Experimental Proof of Concept

        # Strengths & Growth Areas
        strengths = [
          f"Strong domain breadth across {len(user_domains)} key research areas",
          f"Active publication history with {pubs_count} scientific papers and {total_citations} citations",
          f"IP portfolio containing {granted_patents_count} granted patents",
        ]
        growth_areas = [
          "Expand international patent filings (PCT) in target commercial jurisdictions",
          "Accelerate TRL 4-6 prototypes toward field validation and pilot testing",
          "Form industry R&D partnerships to increase technology licensing readiness",
        ]

        summary_text = (
            f"Your Innovation Index is {overall}/100 with an assessed Technology Readiness Level of TRL-{trl}. "
            f"Your research strength ({round(res_score, 1)}) and patent portfolio ({round(pat_score, 1)}) demonstrate high commercialization viability."
        )

        breakdown = InnovationScoreBreakdown(
            publications_count=pubs_count,
            total_citations=total_citations,
            h_index=h_index,
            patents_count=patents_count,
            granted_patents_count=granted_patents_count,
            domains_matched=user_domains,
            technology_interests=user_techs,
            strengths=strengths,
            growth_areas=growth_areas,
        )

        if existing_score:
            existing_score.overall_score = overall
            existing_score.trl_level = trl
            existing_score.research_strength = round(res_score, 1)
            existing_score.patent_strength = round(pat_score, 1)
            existing_score.commercial_potential = round(comm_score, 1)
            existing_score.recommendation_summary = summary_text
            existing_score.breakdown_details = breakdown.model_dump()
            await db.commit()
            await db.refresh(existing_score)
            score_record = existing_score
        else:
            score_record = InnovationScore(
                user_id=user_id,
                overall_score=overall,
                trl_level=trl,
                research_strength=round(res_score, 1),
                patent_strength=round(pat_score, 1),
                commercial_potential=round(comm_score, 1),
                recommendation_summary=summary_text,
                breakdown_details=breakdown.model_dump(),
            )
            db.add(score_record)
            await db.commit()
            await db.refresh(score_record)

        return InnovationScoreResponse(
            id=score_record.id,
            user_id=score_record.user_id,
            overall_score=score_record.overall_score,
            trl_level=score_record.trl_level,
            research_strength=score_record.research_strength,
            patent_strength=score_record.patent_strength,
            commercial_potential=score_record.commercial_potential,
            recommendation_summary=score_record.recommendation_summary,
            breakdown_details=breakdown,
            updated_at=score_record.updated_at,
        )

    @staticmethod
    async def get_opportunity_analysis(
        db: AsyncSession, user_id: uuid.UUID, limit: int = 6
    ) -> OpportunityAnalysisResponse:
        """Analyze high-growth technology gaps and strategic opportunities aligned with user profile."""
        res = await db.execute(
            select(TechnologyTrend).order_by(desc(TechnologyTrend.growth_rate)).limit(limit)
        )
        trends = res.scalars().all()

        opportunities = []
        top_domains = set()
        for idx, t in enumerate(trends):
            alignment = min(round(72.0 + (idx * 4.5), 1), 97.5)
            top_domains.add(t.technology_domain)
            opp = OpportunityAnalysisItem(
                id=t.id,
                title=f"Commercial Opportunity: {t.name}",
                technology_domain=t.technology_domain,
                market_size_usd_b=t.market_size_usd_b,
                growth_rate=t.growth_rate,
                maturity_level=t.maturity_level,
                opportunity_gap=t.opportunity_description,
                alignment_score=alignment,
                recommended_action=f"Initiate R&D project in {t.key_keywords[0] if t.key_keywords else 'Core Tech'} to address market gap of ${t.market_size_usd_b}B.",
                key_keywords=t.key_keywords,
            )
            opportunities.append(opp)

        return OpportunityAnalysisResponse(
            total_opportunities=len(opportunities),
            high_alignment_count=len([o for o in opportunities if o.alignment_score >= 85.0]),
            top_domains=list(top_domains)[:4],
            opportunities=opportunities,
        )

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession, user_id: uuid.UUID
    ) -> TechnologyDashboardSummaryResponse:
        """Construct full Technology Dashboard payload."""
        # Total trends
        total_res = await db.execute(select(func.count(TechnologyTrend.id)))
        total_trends = total_res.scalar_one() or 0

        emerging_res = await db.execute(
            select(func.count(TechnologyTrend.id)).where(TechnologyTrend.is_emerging == True)
        )
        emerging_count = emerging_res.scalar_one() or 0

        avg_growth_res = await db.execute(select(func.avg(TechnologyTrend.growth_rate)))
        avg_growth = round(avg_growth_res.scalar_one() or 30.0, 1)

        # Emerging technologies list
        emerging_list = await TechnologyService.get_emerging_technologies(db, limit=6)

        # Innovation score
        innov_score = await TechnologyService.calculate_user_innovation_score(db, user_id=user_id)

        # Opportunities
        opp_analysis = await TechnologyService.get_opportunity_analysis(db, user_id=user_id, limit=4)

        return TechnologyDashboardSummaryResponse(
            statistics=TechnologyStatisticsSummary(
                total_trends_indexed=total_trends,
                emerging_count=emerging_count,
                avg_growth_rate=avg_growth,
                top_tech_domain="Artificial Intelligence & Machine Learning",
            ),
            emerging_technologies=emerging_list,
            innovation_score=innov_score,
            recommended_opportunities=opp_analysis.opportunities,
        )

    @staticmethod
    async def seed_technology_trends(db: AsyncSession) -> None:
        """Seed 50 realistic technology trend records with TRL levels and market data."""
        existing_res = await db.execute(select(func.count(TechnologyTrend.id)))
        count = existing_res.scalar_one() or 0
        if count >= 50:
            logger.info("Technology trends already seeded (>=50). Skipping.")
            return

        logger.info("Seeding 50 realistic technology trend records for Phase 6...")

        # Sample categories with 5 items each = 50 total records
        categories = [
            # 1. AI & Machine Learning (5 items)
            {
                "domain": "Artificial Intelligence & Machine Learning",
                "items": [
                    ("Agentic Autonomous AI Workflow Orchestration", 6, "TRL 4-6 (Validation & Prototype)", 48.5, 125.4, ["Microsoft", "Google DeepMind", "OpenAI", "Anthropic"], ["Agentic Workflows", "Autonomous AI", "Tool Calling"], True, "Multi-agent systems executing autonomous complex multi-step reasoning.", "High market demand for enterprise autonomous workflow agents replacing manual back-office tasks."),
                    ("Neuromorphic Edge Chips for Low-Power Sensing", 4, "TRL 4-6 (Validation & Prototype)", 36.2, 42.8, ["Intel Labs", "SynSense", "BrainChip", "IBM Research"], ["Neuromorphic Computing", "Spiking Neural Nets", "Ultra-Low Power"], True, "Event-driven spiking neural network ASICs operating under 10 milliwatts.", "Significant gap in wearable health sensors requiring real-time on-device AI inference."),
                    ("Physics-Informed Neural Networks (PINNs) for Fluid Dynamics", 3, "TRL 1-3 (Basic Research)", 41.0, 18.6, ["NVIDIA", "MIT CSAIL", "Stanford AI Lab"], ["PINNs", "Differential Equations", "Physics AI"], True, "Embedding physical conservation laws into neural loss functions for PDE simulation.", "Opportunity in aerospace and automotive aerodynamic testing to reduce wind tunnel costs."),
                    ("Retrieval-Augmented Multimodal Knowledge Graphs", 7, "TRL 7-9 (Commercial Deployment)", 32.8, 95.0, ["Neo4j", "AWS", "Google Cloud", "Databricks"], ["RAG", "Knowledge Graph", "Vector Database"], False, "Hybrid vector database and graph query systems for factual LLM retrieval.", "Commercial gap in enterprise document search with zero-hallucination compliance constraints."),
                    ("Self-Supervised Vision Foundation Models for Robotics", 5, "TRL 4-6 (Validation & Prototype)", 44.1, 78.3, ["Meta AI", "Tesla AI", "Covariant", "Skydio"], ["Vision Foundation Models", "Self-Supervised", "Robotic Perception"], True, "Pretrained 3D spatial vision encoders operating without human-annotated labels.", "Autonomous warehouse robotics seeking universal visual manipulation capabilities."),
                ]
            },
            # 2. Quantum Computing & Information (5 items)
            {
                "domain": "Quantum Computing & Information",
                "items": [
                    ("Logical Qubit Error Correction via Color Codes", 3, "TRL 1-3 (Basic Research)", 52.4, 28.5, ["IBM Quantum", "Google Quantum AI", "QuEra Computing"], ["Logical Qubits", "Color Codes", "Quantum Error Correction"], True, "Executing fault-tolerant logical qubit operations below the physical error threshold.", "Critical path toward commercial quantum simulation of complex drug molecules."),
                    ("Cryogenic CMOS ASIC Controller Arrays", 6, "TRL 4-6 (Validation & Prototype)", 39.8, 14.2, ["Intel", "Equal1", "Seeqc", "Delft University"], ["Cryo-CMOS", "Qubit Control", "Sub-Kelvin Electronics"], False, "Integrating 4K cryogenic control chips inside dilution refrigerators.", "Scaling qubit control from 100 to 10,000+ physical qubits without thermal overload."),
                    ("Quantum Sensing Magnetometers for Brain Imaging (MEG)", 7, "TRL 7-9 (Commercial Deployment)", 28.4, 12.8, ["CNNP", "QDM Labs", "Mag4Health", "Bison Technologies"], ["Quantum Magnetometer", "OPM-MEG", "Room Temp Brain Imaging"], False, "Optically pumped magnetometers mapping cortical neural activity at room temperature.", "Non-invasive neuroimaging replacing liquid-helium MEG scanners in clinical neurology."),
                    ("Photonic Quantum Key Distribution Over Satellite Links", 5, "TRL 4-6 (Validation & Prototype)", 45.0, 22.0, ["ESA", "USTC China", "Toshiba", "ID Quantique"], ["Satellite QKD", "Quantum Cryptography", "Submarine Fiber QKD"], True, "Space-to-ground quantum entangled photon key distribution for global security.", "Governments requiring post-quantum secure communication backbones against eavesdropping."),
                    ("Variational Quantum Algorithms for Financial Portfolio Risk", 4, "TRL 4-6 (Validation & Prototype)", 34.0, 19.5, ["JPMorgan Chase", "Goldman Sachs", "QC Ware", "Zapata AI"], ["VQE", "Quantum Finance", "Monte Carlo Quantum"], False, "Hybrid quantum-classical algorithms solving high-dimensional risk optimization.", "Wall Street funds accelerating derivative pricing calculations on NISQ hardware."),
                ]
            },
            # 3. Biotechnology & Genomics (5 items)
            {
                "domain": "Biotechnology & Genomics",
                "items": [
                    ("CRISPR Base & Prime Editing for In-Vivo Genetic Therapies", 6, "TRL 4-6 (Validation & Prototype)", 42.0, 85.0, ["Broad Institute", "Beam Therapeutics", "Prime Medicine"], ["Base Editing", "Prime Editing", "In-Vivo Gene Therapy"], True, "Single-base precision gene modifications avoiding double-strand DNA breaks.", "Curative single-dose gene editing for rare monogenic liver and blood disorders."),
                    ("Cell-Free Synthetic Biology Enzymatic Reactors", 4, "TRL 4-6 (Validation & Prototype)", 31.5, 38.0, ["Ginkgo Bioworks", "Engeneon", "Amyris", "Evonetix"], ["Cell-Free Biology", "Enzymatic Synthesis", "Biomanufacturing"], False, "Transcription and translation of complex proteins in non-living bio-reactors.", "Rapid continuous synthesis of therapeutic enzymes without cell culture maintenance."),
                    ("Lipid Nanoparticle Targeted Tissue Tropism Delivery", 5, "TRL 4-6 (Validation & Prototype)", 38.6, 64.0, ["Moderna", "BioNTech", "Alnylam", "Arbutus Biopharma"], ["Lipid Nanoparticles", "Targeted LNP", "mRNA Delivery"], True, "Decorating LNP surfaces with peptide ligands targeting non-liver tissue organs.", "Delivering therapeutic mRNA directly to cardiac, lung, and central nervous system cells."),
                    ("Spatial Multi-Omics Microfluidic Profiling Chips", 7, "TRL 7-9 (Commercial Deployment)", 29.0, 48.0, ["10x Genomics", "Vizgen", "NanoString", "Akoya Biosciences"], ["Spatial Genomics", "Single-Cell Multi-Omics", "Microfluidic Chip"], False, "Quantifying RNA transcript and protein spatial coordinates inside histology tissues.", "Oncology research resolving spatial tumor heterogeneity for immunotherapy drug targets."),
                    ("AI-Designed De Novo Synthetic Protein Vaccines", 5, "TRL 4-6 (Validation & Prototype)", 46.2, 54.0, ["Institute for Protein Design", "Generate Biomedicines", "Absci"], ["De Novo Proteins", "Protein Structural Design", "AI Vaccine"], True, "Generative AI designing custom 3D protein nanoparticle cages for pan-virus immunity.", "Rapid pandemic response platforms synthesizing vaccine candidates within 48 hours."),
                ]
            },
            # 4. Clean Energy & Battery Storage (5 items)
            {
                "domain": "Clean Energy & Storage",
                "items": [
                    ("Sulfide Solid-State Lithium Metal EV Batteries", 6, "TRL 4-6 (Validation & Prototype)", 38.4, 180.0, ["Toyota", "QuantumScape", "Solid Power", "Samsung SDI"], ["Solid-State Battery", "Sulfide Electrolyte", "Lithium Metal Anode"], True, "Non-flammable solid electrolytes achieving 500 Wh/kg specific energy density.", "Eliminating EV range anxiety and battery fire risks with 10-minute fast charging."),
                    ("Perovskite-Silicon Tandem Photovoltaic Solar Modules", 7, "TRL 7-9 (Commercial Deployment)", 26.5, 140.0, ["Oxford PV", "Hanwha Qcells", "First Solar", "Longi Solar"], ["Perovskite Solar", "Tandem Photovoltaic", "High Efficiency PV"], False, "Layered solar cells converting over 32% of sunlight into electrical power.", "Utility-scale solar farms generating 30% more power per square meter of land."),
                    ("PEM High-Pressure Water Electrolyzers for Green Hydrogen", 6, "TRL 4-6 (Validation & Prototype)", 35.0, 95.0, ["Plug Power", "ITM Power", "Siemens Energy", "Nel Hydrogen"], ["PEM Electrolyzer", "Green Hydrogen", "Zero Carbon Fuel"], True, "Electrolysis cells generating pure hydrogen gas at 80 bar pressure using renewable power.", "Decarbonizing heavy steel manufacturing, maritime shipping, and chemical plants."),
                    ("Sodium-Ion Grid Energy Storage Batteries", 8, "TRL 7-9 (Commercial Deployment)", 30.2, 110.0, ["CATL", "HiNa Battery", "Natron Energy", "Faradion"], ["Sodium-Ion Battery", "Grid Storage", "Zero Lithium"], False, "Abundant sodium chemistry replacing lithium for stationary utility grid storage.", "Low-cost long-duration battery storage buffering wind and solar intermittent grids."),
                    ("Direct Atmospheric Air Carbon Capture Contactors", 5, "TRL 4-6 (Validation & Prototype)", 41.5, 62.0, ["Climeworks", "Carbon Engineering", "Heirloom", "1pointFive"], ["Direct Air Capture", "Carbon Dioxide Removal", "Sorbent Contactors"], True, "Industrial fans passing ambient air through solid sorbents capturing pure CO2.", "Corporate carbon offset markets removing gigatons of historical atmospheric CO2."),
                ]
            },
            # 5. Cybersecurity & Cryptography (5 items)
            {
                "domain": "Cybersecurity & Cryptography",
                "items": [
                    ("NIST Post-Quantum Lattice Key Exchange Algorithms", 8, "TRL 7-9 (Commercial Deployment)", 33.6, 74.0, ["IBM", "Cloudflare", "Google", "Palo Alto Networks"], ["Post-Quantum Crypto", "Lattice Cryptography", "Kyber Dilithium"], False, "Standardized CRYSTALS-Kyber key encapsulation preventing quantum decryption.", "Upgrading commercial TLS/SSL internet protocols before quantum computer arrival."),
                    ("Hardware-Enforced Confidential Compute Enclaves", 7, "TRL 7-9 (Commercial Deployment)", 28.0, 115.0, ["Intel SGX", "AMD SEV", "AWS Nitro", "NVIDIA H100 Confidential"], ["Confidential Computing", "Hardware Enclave", "Encrypted RAM"], False, "Isolated memory enclaves protecting active data in use from cloud providers.", "Financial and medical institutions training shared AI models on confidential datasets."),
                    ("Zero-Knowledge Rollup Protocols for Distributed Ledgers", 6, "TRL 4-6 (Validation & Prototype)", 44.0, 58.0, ["StarkWare", "Matter Labs", "Polygon zkEVM", "Scroll"], ["zk-Rollups", "Zero-Knowledge Proofs", "Layer-2 Scaling"], True, "Cryptographic proofs batching thousands of transactions off-chain with instant validity.", "High-throughput micro-payments processing 100,000 transactions per second."),
                    ("Continuous Behavioral Biometric Zero-Trust Agents", 6, "TRL 4-6 (Validation & Prototype)", 36.5, 49.0, ["Zscaler", "Okta", "CrowdStrike", "Ping Identity"], ["Zero-Trust", "Behavioral Biometrics", "Continuous Auth"], False, "Monitoring mouse kinematics and touch dynamics to continuously re-verify identity.", "Preventing credential theft and session hijacking in remote workforce environments."),
                    ("Automated Firmware SBOM Security Scanners", 5, "TRL 4-6 (Validation & Prototype)", 39.0, 32.0, ["Finite State", "ReFirm Labs", "Synopsys", "Checkmarx"], ["SBOM Scanner", "Firmware Security", "Supply Chain Audit"], True, "Decompiling binary firmware blobs to audit hidden open-source supply chain vulnerabilities.", "Securing critical IoT infrastructure, medical devices, and automotive ECU firmware."),
                ]
            },
            # 6. Robotics & Autonomous Systems (5 items)
            {
                "domain": "Robotics & Autonomous Systems",
                "orgs": ["Boston Dynamics", "Tesla", "Intuitive Surgical", "FANUC"],
                "items": [
                    ("Whole-Body Model Predictive Control for Humanoid Locomotion", 5, "TRL 4-6 (Validation & Prototype)", 47.8, 88.0, ["Boston Dynamics", "Tesla Optimus", "Figure AI", "Agility Robotics"], ["Humanoid Robot", "Model Predictive Control", "Bipedal Balance"], True, "Real-time physics engines optimizing 30+ joint actuators for dynamic stair climbing.", "Deploying general-purpose humanoid workers in automotive assembly lines."),
                    ("Fiber-Optic Haptic Feedback Surgical Manipulators", 7, "TRL 7-9 (Commercial Deployment)", 27.4, 65.0, ["Intuitive Surgical", "Medtronic", "Johnson & Johnson", "Asensus"], ["Surgical Robotics", "Haptic Sensing", "Fiber-Bragg Sensors"], False, "Fiber-Bragg grating arrays giving surgeons tactile force feedback during laparoscopic procedures.", "Improving surgical accuracy and reducing tissue damage during minimally invasive procedures."),
                    ("Autonomous Aerial Swarm Mesh Collision Avoidance", 5, "TRL 4-6 (Validation & Prototype)", 41.0, 36.0, ["Skydio", "Anduril", "Elbit Systems", "DJI"], ["Drone Swarm", "Mesh Networking", "Decentralized SLAM"], True, "Decentralized radio protocols coordinating 100+ drones without GPS or ground control.", "Search and rescue operations in GPS-denied collapsed buildings and dense forests."),
                    ("Pneumatic Soft Robotic Actuators for Delicate Harvesting", 6, "TRL 4-6 (Validation & Prototype)", 33.5, 29.0, ["Soft Robotics Inc", "Rippl", "Abundant Robotics", "Four Growers"], ["Soft Robotics", "Elastomer Actuator", "Agri Harvesting"], False, "Deformable silicone fingers gripping fragile berries and tomatoes without bruising.", "Addressing severe agricultural labor shortages during peak harvesting seasons."),
                    ("Solid-State Flash LiDAR Perceptors for Autonomous Mobility", 8, "TRL 7-9 (Commercial Deployment)", 31.0, 92.0, ["Luminar", "Innoviz", "Hesai", "Velodyne"], ["Solid-State LiDAR", "Flash LiDAR", "3D Perception"], False, "No-moving-parts 1550nm laser sensors detecting dark objects at 250 meters distance.", "Enabling Level 3 and Level 4 autonomous highway driving under adverse weather."),
                ]
            },
            # 7. Semiconductors & Microelectronics (5 items)
            {
                "domain": "Semiconductors & Microelectronics",
                "items": [
                    ("Sub-2nm Gate-All-Around Nanosheet RibbonFETs", 6, "TRL 4-6 (Validation & Prototype)", 36.0, 210.0, ["TSMC", "Intel", "Samsung Foundry", "IBM"], ["GAAFET", "Nanosheet", "RibbonFET 2nm"], True, "Multi-stacked silicon nanosheets wrapped 360-degrees by gate dielectrics.", "Maintaining Moore's Law scaling for next-generation mobile and AI supercomputing."),
                    ("High-NA Extreme Ultraviolet (EUV) Lithography Systems", 8, "TRL 7-9 (Commercial Deployment)", 24.5, 175.0, ["ASML", "Zeiss", "Applied Materials", "Tokyo Electron"], ["High-NA EUV", "0.55 NA", "Sub-2nm Patterning"], False, "0.55 numerical aperture EUV scanners printing 8nm single-exposure feature pitches.", "Manufacturing sub-2nm chipsets without expensive multi-patterning mask steps."),
                    ("3D Heterogeneous Chiplet Silicon Interposers", 8, "TRL 7-9 (Commercial Deployment)", 32.0, 145.0, ["TSMC CoWoS", "Intel EMIB", "ASE Group", "Amkor"], ["3D Packaging", "Chiplet Interposer", "Micro-Bumps"], False, "High-density micro-bump substrates linking GPU dies, HBM3 memory, and I/O chiplets.", "Building massive 100-billion transistor AI processors with high silicon yields."),
                    ("Gallium Nitride (GaN) on Silicon Power Switch Semiconductors", 8, "TRL 7-9 (Commercial Deployment)", 28.5, 68.0, ["Navitas", "GaN Systems", "Infineon", "STMicroelectronics"], ["GaN Power", "Wide Bandgap", "High Efficiency Power"], False, "Wide-bandgap transistors switching at megahertz frequencies with 99% energy efficiency.", "Shrinking laptop chargers and EV onboard power converters by 50% in physical volume."),
                    ("Sub-Nanosecond Spin-Orbit Torque MRAM Arrays", 4, "TRL 1-3 (Basic Research)", 43.2, 26.0, ["Everspin", "Spin Memory", "Imec", "Tohoku University"], ["SOT-MRAM", "Spin-Orbit Torque", "Non-Volatile RAM"], True, "Writing magnetic states via heavy-metal spin currents with sub-nanosecond latency.", "Replacing volatile SRAM cache memories in CPUs with zero standby leakage power."),
                ]
            },
            # 8. MedTech & Medical Devices (5 items)
            {
                "domain": "MedTech & Medical Devices",
                "items": [
                    ("Subcutaneous Continuous Optical Glucose Sensors", 7, "TRL 7-9 (Commercial Deployment)", 29.5, 82.0, ["Dexcom", "Abbott FreeStyle", "Senseonics", "Medtronic"], ["CGM Sensor", "Continuous Glucose", "Optical Fluorescence"], False, "Fluorescent hydrogel polymers measuring interstitial fluid glucose for 180 days.", "Painless continuous diabetes monitoring without frequent sensor replacement needles."),
                    ("Directional Deep Brain Stimulation (DBS) Electrodes", 7, "TRL 7-9 (Commercial Deployment)", 26.0, 44.0, ["Medtronic", "Boston Scientific", "Abbott Neuromodulation"], ["DBS Lead", "Directional Neurostimulation", "Parkinsons Therapy"], False, "Segmented 8-channel leads shaping electrical stimulation fields precisely into brain nuclei.", "Suppressing Parkinsonian tremor symptoms while minimizing side-effect speech impairment."),
                    ("Ultra-High Field 7-Tesla Brain MRI Scanners", 7, "TRL 7-9 (Commercial Deployment)", 23.0, 38.0, ["Siemens Healthineers", "GE HealthCare", "Philips Healthcare"], ["7T MRI", "Ultra-High Field MRI", "Neurovascular Imaging"], False, "7-Tesla magnetic fields resolving sub-millimeter brain tissue structures and blood vessels.", "Early detection of Alzheimer's amyloid plaques and multiple sclerosis lesions."),
                    ("Automated Dual-Hormone Closed-Loop Artificial Pancreas", 6, "TRL 4-6 (Validation & Prototype)", 37.5, 52.0, ["Beta Bionics", "Insulet", "Tandem Diabetes", "University of Virginia"], ["Artificial Pancreas", "Closed-Loop Insulin", "Dual Hormone Glucagon"], True, "Control algorithms pumping insulin and glucagon dynamically to prevent hypoglycemia.", "Fully automated blood sugar management eliminating manual carb counting for patients."),
                    ("Bioresorbable Poly-L-Lactic Acid Coronary Stents", 6, "TRL 4-6 (Validation & Prototype)", 32.0, 31.0, ["Abbott", "REVA Medical", "Biotronik", "Elixir Medical"], ["Bioresorbable Stent", "Dissolving Scaffold", "Coronary Artery"], False, "Polylactic acid artery scaffolds restoring vessel tone then dissolving fully in 24 months.", "Preventing permanent metallic stent implant complications in young cardiac patients."),
                ]
            },
            # 9. Wireless Communications & 6G (5 items)
            {
                "domain": "Wireless Communications & 6G",
                "items": [
                    ("Sub-THz 140GHz Reconfigurable Intelligent Metasurfaces", 4, "TRL 1-3 (Basic Research)", 51.0, 64.0, ["Nokia Bell Labs", "Qualcomm", "NTT Docomo", "Samsung Research"], ["6G Sub-THz", "RIS Metasurface", "140GHz Wireless"], True, "Active meta-reflectors steering sub-terahertz radio beams around urban buildings.", "Achieving 100 Gigabits per second wireless connectivity in dense stadium environments."),
                    ("Integrated Sensing and Communication (JCAS) Waveforms", 5, "TRL 4-6 (Validation & Prototype)", 43.5, 48.0, ["Ericsson", "Huawei", "ZTE", "InterDigital"], ["JCAS", "Radar Waveform", "6G Sensing"], True, "Unified OFDM frames acting simultaneously as 6G cellular carrier and 3D radar mapper.", "Enabling cellular towers to track drone flights and vehicle traffic without separate radar."),
                    ("Photonic-Assisted 300GHz Wireless Terahertz Front-Ends", 3, "TRL 1-3 (Basic Research)", 49.0, 21.0, ["Fraunhofer IAF", "University of Tokyo", "Thales", "Keysight"], ["Photonic THz", "300GHz Wireless", "Laser Heterodyne"], True, "Optical heterodyne lasers generating sub-millimeter wireless carrier waves.", "Sub-millisecond data center server rack interconnects without fiber patch cords."),
                    ("Cell-Free Distributed Massive MIMO Transceivers", 6, "TRL 4-6 (Validation & Prototype)", 37.0, 56.0, ["Ericsson", "Nokia", "Samsung", "Linköping University"], ["Cell-Free MIMO", "Distributed Access Points", "Massive MIMO"], False, "Coordinating 64 distributed access points as a single coherent wireless transceiver.", "Eliminating coverage drop-offs at cell tower boundaries in high-speed rail lines."),
                    ("Deep Learning Semantic Source-Channel Audio Codecs", 5, "TRL 4-6 (Validation & Prototype)", 45.2, 33.0, ["Qualcomm AI", "DeepMind", "Meta AI", "Sony Research"], ["Semantic Codec", "Deep Joint Source-Channel", "AI Audio"], True, "Transmitting low-dimensional neural latent vectors reconstructed into crystal audio.", "Streaming high-fidelity voice calls over severely congested 1% bandwidth channels."),
                ]
            },
            # 10. Autonomous Vehicles & Space Mobility (5 items)
            {
                "domain": "Autonomous Vehicles & Space Mobility",
                "items": [
                    ("4D Digital Imaging Radar with Elevation Resolution", 7, "TRL 7-9 (Commercial Deployment)", 34.0, 72.0, ["Arbe Robotics", "NXP", "Bosch", "Continental"], ["4D Radar", "Imaging Radar", "Elevation Sensing"], False, "High-resolution radar arrays measuring object velocity, azimuth, and height in rain.", "Preventing highway accidents under heavy fog, snowstorms, and blinding sun glare."),
                    ("Sub-Centimeter Ultrawideband (UWB) Automated Valet Positioning", 7, "TRL 7-9 (Commercial Deployment)", 29.0, 41.0, ["Waymo", "Cruise", "NVIDIA DRIVE", "Valeo"], ["UWB Valet", "Automated Valet Parking", "Indoor Positioning"], False, "Garages fitted with UWB radio anchors guiding vehicles into micro-parking spots.", "Self-parking vehicles operating smoothly inside subterranean multi-story concrete structures."),
                    ("Thermal Infrared Night Vision Perception Pipelines", 6, "TRL 4-6 (Validation & Prototype)", 39.5, 38.0, ["Teledyne FLIR", "Owl Autonomous", "ADASKY", "Magna"], ["Thermal IR", "Night Perception", "Long-Wave IR"], True, "Long-wave thermal sensors picking up pedestrian heat signatures 300 meters away.", "Protecting pedestrians at night when high-beam headlights fail to illuminate hazards."),
                    ("Spacecraft Methane-LOX Autogenous Pressurization Engines", 8, "TRL 7-9 (Commercial Deployment)", 31.5, 120.0, ["SpaceX Raptor", "Blue Origin BE-4", "Rocket Lab", "Relativity Space"], ["Methane LOX", "Autogenous Pressurization", "Reusable Rocket"], False, "Gas-gas combustion cycles eliminating helium tank pressurization for rapid reusable rockets.", "Lowering space launch costs to under $1,000 per kilogram to low Earth orbit."),
                    ("Autonomous In-Space Robotic Satellite Refueling Arms", 5, "TRL 4-6 (Validation & Prototype)", 46.0, 52.0, ["Astroscale", "Northrop Grumman OrbitFab", "MDA Space", "ClearSpace"], ["In-Space Servicing", "Satellite Refueling", "Orbital Robotics"], True, "Space manipulators docking with non-cooperative satellites to replenish hydrazine propellant.", "Extending operational lifespan of $500M geostationary telecom satellites by 10 years."),
                ]
            }
        ]

        records = []
        for cat in categories:
            dom = cat["domain"]
            for name, trl, maturity, growth, mkt, players, kws, emerging, summary, opp in cat["items"]:
                rec = TechnologyTrend(
                    name=name,
                    technology_domain=dom,
                    trl_level=trl,
                    maturity_level=maturity,
                    growth_rate=growth,
                    market_size_usd_b=mkt,
                    key_players=players,
                    key_keywords=kws,
                    is_emerging=emerging,
                    summary=summary,
                    opportunity_description=opp,
                    year=2025,
                )
                records.append(rec)

        db.add_all(records)
        await db.commit()
        logger.info(f"Successfully seeded {len(records)} technology trends!")
