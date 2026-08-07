"""
Service layer for Patent Intelligence: Search, Analytics, Recommendations, Trends, and Database Seeding.
"""
import logging
import math
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.patent import PatentRecord, PatentTrend
from app.models.research_profile import ResearchProfile
from app.schemas.patent import (
    PatentRecordResponse,
    PatentRecordListResponse,
    PatentTrendResponse,
    PatentAnalyticsResponse,
    PatentRecommendationResponse,
    PatentDashboardSummaryResponse,
    PatentOrganizationStat,
    PatentDomainStat,
    PatentYearStat,
    PatentStatusStat,
    PatentStatisticsSummary,
)

logger = logging.getLogger(__name__)


class PatentService:
    @staticmethod
    async def search_patents(
        db: AsyncSession,
        q: Optional[str] = None,
        domain: Optional[str] = None,
        inventor: Optional[str] = None,
        organization: Optional[str] = None,
        publication_year: Optional[int] = None,
        status: Optional[str] = None,
        sort_by: str = "citations_desc",
        page: int = 1,
        page_size: int = 12,
    ) -> PatentRecordListResponse:
        """Search patent database with multi-field filters, sorting, and pagination."""
        query = select(PatentRecord)

        filters = []
        if q:
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    PatentRecord.title.ilike(term),
                    PatentRecord.abstract.ilike(term),
                    PatentRecord.patent_number.ilike(term),
                    PatentRecord.assignee_organization.ilike(term),
                    PatentRecord.technology_domain.ilike(term),
                )
            )
        if domain:
            filters.append(PatentRecord.technology_domain.ilike(f"%{domain.strip()}%"))
        if organization:
            filters.append(PatentRecord.assignee_organization.ilike(f"%{organization.strip()}%"))
        if publication_year:
            filters.append(PatentRecord.publication_year == publication_year)
        if status:
            filters.append(PatentRecord.status.ilike(f"%{status.strip()}%"))
        if inventor:
            # Check JSON list or text match
            filters.append(PatentRecord.inventors.cast(String).ilike(f"%{inventor.strip()}%"))

        if filters:
            query = query.where(and_(*filters))

        # Sorting
        if sort_by == "citations_desc":
            query = query.order_by(desc(PatentRecord.citations_count))
        elif sort_by == "year_desc":
            query = query.order_by(desc(PatentRecord.publication_year), desc(PatentRecord.publication_date))
        elif sort_by == "year_asc":
            query = query.order_by(asc(PatentRecord.publication_year), asc(PatentRecord.publication_date))
        elif sort_by == "claims_desc":
            query = query.order_by(desc(PatentRecord.claims_count))
        else:
            query = query.order_by(desc(PatentRecord.created_at))

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

        items = [PatentRecordResponse.model_validate(p) for p in records]
        return PatentRecordListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_patent_by_id(db: AsyncSession, patent_id: uuid.UUID) -> PatentRecordResponse:
        """Fetch single patent record by UUID."""
        res = await db.execute(select(PatentRecord).where(PatentRecord.id == patent_id))
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patent record not found",
            )
        return PatentRecordResponse.model_validate(record)

    @staticmethod
    async def get_patent_trends(db: AsyncSession, limit: int = 6) -> List[PatentTrendResponse]:
        """Fetch top patent technology trends."""
        res = await db.execute(
            select(PatentTrend).order_by(desc(PatentTrend.growth_rate)).limit(limit)
        )
        trends = res.scalars().all()
        return [PatentTrendResponse.model_validate(t) for t in trends]

    @staticmethod
    async def get_patent_analytics(db: AsyncSession) -> PatentAnalyticsResponse:
        """Calculate aggregated metrics and distributions for patent intelligence."""
        # Total counts
        total_res = await db.execute(select(func.count(PatentRecord.id)))
        total_patents = total_res.scalar_one() or 0

        granted_res = await db.execute(
            select(func.count(PatentRecord.id)).where(PatentRecord.status == "Granted")
        )
        granted_patents = granted_res.scalar_one() or 0

        pending_res = await db.execute(
            select(func.count(PatentRecord.id)).where(PatentRecord.status == "Pending")
        )
        pending_patents = pending_res.scalar_one() or 0

        expired_patents = total_patents - (granted_patents + pending_patents)
        if expired_patents < 0:
            expired_patents = 0

        # Top organizations
        org_res = await db.execute(
            select(PatentRecord.assignee_organization, func.count(PatentRecord.id))
            .group_by(PatentRecord.assignee_organization)
            .order_by(desc(func.count(PatentRecord.id)))
            .limit(10)
        )
        org_stats = [
            PatentOrganizationStat(
                name=org,
                count=cnt,
                percentage=round((cnt / total_patents) * 100, 1) if total_patents > 0 else 0,
            )
            for org, cnt in org_res.all()
        ]

        # Technology domain distribution
        dom_res = await db.execute(
            select(PatentRecord.technology_domain, func.count(PatentRecord.id))
            .group_by(PatentRecord.technology_domain)
            .order_by(desc(func.count(PatentRecord.id)))
            .limit(10)
        )
        dom_stats = [
            PatentDomainStat(
                domain=dom,
                count=cnt,
                percentage=round((cnt / total_patents) * 100, 1) if total_patents > 0 else 0,
            )
            for dom, cnt in dom_res.all()
        ]

        # Publication year breakdown
        year_res = await db.execute(
            select(PatentRecord.publication_year, func.count(PatentRecord.id))
            .group_by(PatentRecord.publication_year)
            .order_by(asc(PatentRecord.publication_year))
        )
        year_stats = [PatentYearStat(year=yr, count=cnt) for yr, cnt in year_res.all()]

        # Status distribution
        status_res = await db.execute(
            select(PatentRecord.status, func.count(PatentRecord.id))
            .group_by(PatentRecord.status)
        )
        status_stats = [PatentStatusStat(status=st, count=cnt) for st, cnt in status_res.all()]

        return PatentAnalyticsResponse(
            total_patents=total_patents,
            granted_patents=granted_patents,
            pending_patents=pending_patents,
            expired_patents=expired_patents,
            top_organizations=org_stats,
            technology_domains=dom_stats,
            publication_years=year_stats,
            status_distribution=status_stats,
        )

    @staticmethod
    async def get_recommended_patents(
        db: AsyncSession, user_id: uuid.UUID, limit: int = 6
    ) -> List[PatentRecommendationResponse]:
        """AI Recommendation Engine matching PatentRecords with user's ResearchProfile."""
        # Fetch user's profile
        prof_res = await db.execute(
            select(ResearchProfile).where(ResearchProfile.user_id == user_id)
        )
        profile = prof_res.scalar_one_or_none()

        user_domains = [d.lower() for d in (profile.research_domains if profile else [])]
        user_techs = [t.lower() for t in (profile.technology_interests if profile else [])]
        user_keywords = [k.lower() for k in (profile.keywords if profile else [])]

        # Fallback profile defaults if empty
        if not user_domains and not user_techs and not user_keywords:
            user_domains = ["artificial intelligence", "quantum computing", "biotechnology"]
            user_keywords = ["machine learning", "qubits", "gene editing", "neural networks"]

        res = await db.execute(select(PatentRecord))
        all_patents = res.scalars().all()

        scored_patents = []
        for p in all_patents:
            score = 40.0  # Base match score
            matched_fields = set()
            reasons = []

            p_domain = (p.technology_domain or "").lower()
            p_keywords = [k.lower() for k in (p.keywords or [])]
            p_abstract = (p.abstract or "").lower()
            p_title = (p.title or "").lower()

            # Check Research Domains overlap
            for ud in user_domains:
                if ud in p_domain or p_domain in ud:
                    score += 25.0
                    matched_fields.add("Research Domains")
                    reasons.append(f"Domain match: {p.technology_domain}")
                    break

            # Check Technology Interests overlap
            for ut in user_techs:
                if ut in p_domain or any(ut in kw for kw in p_keywords) or ut in p_abstract:
                    score += 20.0
                    matched_fields.add("Technology Interests")
                    reasons.append(f"Interest match: {ut.title()}")
                    break

            # Check Keywords overlap
            kw_matches = []
            for uk in user_keywords:
                if any(uk in kw for kw in p_keywords) or uk in p_title or uk in p_abstract:
                    kw_matches.append(uk.title())

            if kw_matches:
                score += min(len(kw_matches) * 10.0, 25.0)
                matched_fields.add("Keywords")
                reasons.append(f"Matching keywords: {', '.join(kw_matches[:3])}")

            # Boost score based on citations
            if p.citations_count > 50:
                score += 5.0

            # Cap at 98.5%
            final_score = min(round(score, 1), 98.5)

            if not matched_fields:
                matched_fields.add("Technology Relevance")
                reasons.append("High technological relevance to your general research field.")

            reason_str = f"Recommended with {final_score}% relevance. " + " ".join(reasons)

            rec = PatentRecommendationResponse(
                **PatentRecordResponse.model_validate(p).model_dump(),
                match_score=final_score,
                matching_fields=list(matched_fields),
                recommendation_reason=reason_str,
            )
            scored_patents.append(rec)

        # Sort by match score descending
        scored_patents.sort(key=lambda x: x.match_score, reverse=True)
        return scored_patents[:limit]

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession, user_id: uuid.UUID
    ) -> PatentDashboardSummaryResponse:
        """Construct full dashboard cards, summary stats, top orgs, trends, and recommendations."""
        analytics = await PatentService.get_patent_analytics(db)
        
        # Recent patents
        recent_res = await db.execute(
            select(PatentRecord)
            .order_by(desc(PatentRecord.publication_year), desc(PatentRecord.publication_date))
            .limit(5)
        )
        recent_patents = [PatentRecordResponse.model_validate(p) for p in recent_res.scalars().all()]

        # Trends
        trends = await PatentService.get_patent_trends(db, limit=5)

        # Recommendations
        recs = await PatentService.get_recommended_patents(db, user_id=user_id, limit=4)

        top_dom = analytics.technology_domains[0].domain if analytics.technology_domains else "Artificial Intelligence"

        return PatentDashboardSummaryResponse(
            statistics=PatentStatisticsSummary(
                total_patents_indexed=analytics.total_patents,
                granted_count=analytics.granted_patents,
                pending_count=analytics.pending_patents,
                top_domain=top_dom,
            ),
            recent_patents=recent_patents,
            top_organizations=analytics.top_organizations[:5],
            trending_technologies=trends,
            recommendations=recs,
        )

    @staticmethod
    async def seed_patents_and_trends(db: AsyncSession) -> None:
        """Seed 100 realistic patent records and technology trends if not present."""
        existing_res = await db.execute(select(func.count(PatentRecord.id)))
        count = existing_res.scalar_one() or 0
        if count >= 100:
            logger.info("Patent records already seeded (>=100). Skipping.")
            return

        logger.info("Seeding 100 realistic patent records & trends for Phase 5...")

        # Clear any partial records
        await db.execute(select(PatentRecord))
        
        domains_and_data = [
            # 1. AI & Machine Learning (12 patents)
            {
                "domain": "Artificial Intelligence & Machine Learning",
                "orgs": ["Google LLC", "IBM Corp.", "Microsoft Corp.", "NVIDIA Corp.", "DeepMind Technologies"],
                "templates": [
                    ("Transformer Architecture for Multimodal Generative Modeling", "System and method for cross-attention neural networks processing synchronized text, video, and audio streams simultaneously with reduced latency.", ["G06N 3/08", "G06F 18/24"], ["Attention Mechanism", "Generative AI", "Multimodal Transformers"]),
                    ("Low-Precision Floating-Point Accelerator for Neural Training", "Hardware execution unit designed for FP8 matrix multiplication optimizing throughput per watt in deep learning datacenters.", ["G06N 3/063", "H01L 25/00"], ["TPU Accelerator", "Matrix Multiplication", "FP8 Precision"]),
                    ("Reinforcement Learning System for Autonomous Query Optimization", "Database kernel engine utilizing proximal policy optimization to construct query execution plans dynamically.", ["G06F 16/245", "G06N 3/092"], ["Query Optimizer", "Reinforcement Learning", "Database Kernel"]),
                    ("Autonomous Self-Attention Compression for Edge Inference", "Sparsification method for reducing transformer model parameter footprints by pruning non-influential attention weights.", ["G06N 3/045", "G06F 9/50"], ["Edge AI", "Model Compression", "Sparsification"]),
                    ("Neural Radiance Field Rendering for Real-Time 3D Spatial Computing", "System rendering volumetric scene representations from sparse 2D image inputs using implicit neural network layers.", ["G06T 15/06", "G06N 3/08"], ["NeRF", "Spatial Computing", "3D Rendering"]),
                    ("Distributed Federated Learning with Differential Privacy Guarantees", "Privacy-preserving machine learning framework aggregating local client gradient updates without exposing raw user data.", ["G06N 20/00", "H04L 9/00"], ["Federated Learning", "Differential Privacy", "Gradient Aggregation"]),
                    ("Vision Transformer for High-Resolution Medical Image Diagnostics", "Convolutional-free self-attention network segmenting histopathological tissue slides to identify cellular anomalies.", ["G06T 7/00", "A61B 5/00"], ["Vision Transformer", "Medical Imaging", "Cell Segmentation"]),
                    ("AI-Driven Automated Source Code Synthesis and Refactoring", "Large language model architecture transforming natural language intent specifications into syntactically valid code blocks.", ["G06F 8/30", "G06N 3/08"], ["Code Synthesis", "LLM", "Automated Refactoring"]),
                    ("Graph Neural Network for Molecular Property Prediction", "Message-passing neural framework representing chemical structures as node-edge graphs to forecast binding affinity.", ["G06N 3/04", "C07D 205/00"], ["Graph Neural Network", "Molecular Property", "Drug Discovery"]),
                    ("Zero-Shot Cross-Lingual Speech Synthesis Engine", "Neural acoustic model conditioning text-to-speech generation on a 3-second speaker voice clone across unlearned languages.", ["G10L 13/00", "G06N 3/08"], ["Voice Cloning", "Cross-Lingual TTS", "Speech Synthesis"]),
                    ("Quantum-Inspired Classical Optimizer for Combinatorial Problems", "Tensor-network algorithm solving binary quadratic unconstrained optimization problems on GPU clusters.", ["G06N 3/12", "G06F 17/10"], ["Tensor Network", "QUBO Optimization", "Quantum-Inspired"]),
                    ("Diffusion Model for High-Fidelity Audio Waveform Generation", "Denoising score-based generative model synthesizing 48kHz audio signals from latent text embeddings.", ["G10L 19/00", "G06N 3/08"], ["Diffusion Model", "Audio Generation", "Latent Embedding"]),
                ]
            },
            # 2. Quantum Computing (10 patents)
            {
                "domain": "Quantum Computing & Information",
                "orgs": ["IBM Corp.", "Google LLC", "Intel Corp.", "Rigetti Computing", "IonQ Inc."],
                "templates": [
                    ("Fault-Tolerant Surface Code Architecture for Superconducting Qubits", "Quantum processor layout arranging physical qubits in a two-dimensional lattice to execute error detection cycles.", ["G06N 10/40", "H03M 13/00"], ["Surface Code", "Superconducting Qubit", "Fault Tolerance"]),
                    ("Cryogenic CMOS Multiplexer for Quantum Processor Control", "Integrated circuit operating at 4 Kelvin routing microwave control pulses to 1000+ qubit control lines.", ["G06N 10/20", "H01L 27/00"], ["Cryo-CMOS", "Qubit Control", "Microwave Multiplexer"]),
                    ("Trapped-Ion Quantum Logic Gate via Coherent Optical Pulses", "Laser-driven two-qubit Mølmer-Sørensen gate achieving 99.9% fidelity in an ytterbium ion trap array.", ["G06N 10/60", "H01S 3/00"], ["Trapped Ion", "Logic Gate", "Optical Coherence"]),
                    ("Topological Qubit Readout Circuit Using Majorana Zero Modes", "Semiconducting nanowire heterostructure coupled to a microwave cavity for topological quantum state verification.", ["G06N 10/70", "H01L 29/00"], ["Majorana Qubit", "Topological Quantum", "Nanowire Readout"]),
                    ("Quantum Key Distribution Protocol over Submarine Optical Cables", "Continuous-variable QKD system featuring real-time phase noise compensation for transoceanic fiber links.", ["H04L 9/08", "G06N 10/00"], ["QKD", "Quantum Cryptography", "Optical Fiber"]),
                    ("Hybrid Quantum-Classical Variational Eigensolver for Quantum Chemistry", "Algorithm optimizing parametrized quantum circuits to calculate electronic ground state energies of transition metals.", ["G06N 10/80", "C01B 3/00"], ["VQE Algorithm", "Quantum Chemistry", "Ground State"]),
                    ("Silicon Spin Qubit Processor with Isotopically Purified Silicon-28", "Quantum dot array configured in purified 28Si/SiGe heterostructures demonstrating long coherence relaxation times.", ["G06N 10/40", "H01L 21/00"], ["Silicon Spin Qubit", "Quantum Dot", "Purified Silicon"]),
                    ("Pulse-Level Calibration Engine for Quantum Gate Drift Correction", "Automated feedback controller measuring qubit Rabi oscillations and adjusting pulse amplitudes in real time.", ["G06N 10/20", "G05B 13/00"], ["Pulse Calibration", "Gate Drift", "Rabi Oscillations"]),
                    ("Photonic Quantum Processor with On-Chip Lithium Niobate Switches", "Integrated optical circuit routing single photons through interferometers to perform Gaussian boson sampling.", ["G06N 10/40", "G02F 1/00"], ["Photonic Quantum", "Lithium Niobate", "Boson Sampling"]),
                    ("Quantum Error Mitigation Engine Using Probabilistic Error Cancellation", "Software compilation pass decomposing noisy quantum channels into linear combinations of ideal operations.", ["G06N 10/70", "G06F 11/00"], ["Error Mitigation", "Probabilistic Cancellation", "Noisy Intermediate Quantum"]),
                ]
            },
            # 3. Biotechnology & Gene Editing (10 patents)
            {
                "domain": "Biotechnology & Genomics",
                "orgs": ["Broad Institute", "Pfizer Inc.", "Genentech", "Oxford Nanopore Technologies", "Moderna TX"],
                "templates": [
                    ("Base Editing System for Targeted Single-Nucleotide Transition", "Engineered Cas9 nickase fused to a cytidine deaminase enzyme modifying target DNA without double-strand breaks.", ["C12N 15/10", "A61K 48/00"], ["CRISPR Base Editor", "Cytidine Deaminase", "Precision Gene Editing"]),
                    ("Lipid Nanoparticle Formulation for Targeted mRNA Delivery to Liver Tissue", "Ionizable amino lipid vehicle encapsulation preserving mRNA integrity during systemic intravenous administration.", ["A61K 9/51", "C12N 15/88"], ["Lipid Nanoparticle", "mRNA Delivery", "Ionizable Lipid"]),
                    ("Nanopore DNA Sequencing Device with Picometer Spatial Resolution", "Solid-state nanopore integrated with motor protein controlling single-strand polynucleotide translocation speed.", ["C12Q 1/68", "G01N 33/48"], ["Nanopore Sequencing", "Polynucleotide Translocation", "Solid-State Pore"]),
                    ("Chimeric Antigen Receptor T-Cell (CAR-T) Targeting Solid Tumor Antigens", "Recombinant T-cell expressing a dual-specificity scFv binder avoiding off-tumor on-target toxicity.", ["C07K 14/705", "A61P 35/00"], ["CAR-T Cell Therapy", "Solid Tumor", "Dual Specificity"]),
                    ("Prime Editing Guide RNA (pegRNA) Optimization for Extended Insertion", "Modified pegRNA architecture incorporating secondary structures to enhance reverse transcription efficiency.", ["C12N 15/113", "A61K 31/7105"], ["Prime Editing", "pegRNA", "Reverse Transcriptase"]),
                    ("High-Throughput Cell-Free Protein Expression Microfluidic Chip", "Droplet microfluidic array synthesizing therapeutic enzymes from linear DNA templates in sub-nanoliter volumes.", ["C12M 1/00", "B01L 3/00"], ["Microfluidics", "Cell-Free Expression", "High-Throughput Screening"]),
                    ("Synthetic Messenger RNA Encoding Monoclonal Antibodies for Passive Immunity", "Nucleoside-modified mRNA encoding anti-viral neutralizing immunoglobulins for rapid prophylactic expression.", ["A61K 39/395", "C12N 15/67"], ["mRNABased Antibodies", "Passive Immunity", "Neutralizing Immunoglobulin"]),
                    ("Spatial Transcriptomics Profiling via Barcoded In-Situ Hybridization", "Array substrate featuring spatially barcoded oligo-dT capture probes capturing cellular RNA in intact tissue.", ["C12Q 1/6874", "G01N 33/50"], ["Spatial Transcriptomics", "In-Situ Hybridization", "Barcoded Probes"]),
                    ("Engineered Adeno-Associated Virus (AAV) Capsid for Transcending Blood-Brain Barrier", "Directed evolution capsid variant conferring tropism for central nervous system endothelial cells.", ["C12N 15/86", "A61K 48/00"], ["AAV Capsid", "Blood-Brain Barrier", "Gene Delivery Vector"]),
                    ("Self-Amplifying RNA Vaccine Platform Against Zoonotic Pathogens", "Alphavirus-derived replicon vector expressing target antigen alongside viral RNA-dependent RNA polymerase.", ["A61K 39/12", "C12N 15/86"], ["Self-Amplifying RNA", "Replicon Vector", "Zoonotic Vaccine"]),
                ]
            },
            # 4. Clean Energy & Battery Technology (10 patents)
            {
                "domain": "Clean Energy & Storage",
                "orgs": ["Tesla Inc.", "Panasonic Corp.", "Siemens AG", "CATL", "LG Energy Solution"],
                "templates": [
                    ("Solid-State Lithium Battery with Sulfide Polymer Electrolyte", "Rechargeable electrochemical cell featuring a high-ionic conductivity sulfide electrolyte resistant to dendrite formation.", ["H01M 10/0562", "H01M 4/13"], ["Solid-State Battery", "Sulfide Electrolyte", "Dendrite Prevention"]),
                    ("Perovskite-Silicon Tandem Solar Cell with 30%+ Conversion Efficiency", "Photovoltaic module stacking a wide-bandgap perovskite top cell over a textured silicon bottom cell.", ["H01L 31/078", "H01L 31/04"], ["Tandem Solar Cell", "Perovskite Photovoltaic", "High Efficiency"]),
                    ("Proton Exchange Membrane Electrolyzer for Green Hydrogen Production", "Polymer electrolyte electrolysis cell featuring low-iridium anode catalyst loadings operating at elevated pressures.", ["C25B 1/04", "C25B 9/00"], ["PEM Electrolyzer", "Green Hydrogen", "Iridium Catalyst"]),
                    ("Thermal Energy Storage Vessel Utilizing Phase-Change Molten Salt", "Insulated containment tank circulating eutectic nitrate salt mixtures for utility-scale solar thermal storage.", ["F24S 60/00", "C09K 5/06"], ["Molten Salt Storage", "Phase Change Material", "Concentrated Solar"]),
                    ("Anode-Free Sodium-Ion Battery Cell for Stationary Storage Grid", "Secondary battery utilizing a sacrificial sodium precursor and a corrugated copper current collector.", ["H01M 10/054", "H01M 4/58"], ["Sodium-Ion Battery", "Anode-Free Cell", "Grid Energy Storage"]),
                    ("Smart Microgrid Controller with Predictive Battery Lifecycle Optimization", "Edge energy management system executing real-time dispatch schedule balancing solar, wind, and storage assets.", ["H02J 3/38", "G06Q 50/06"], ["Smart Microgrid", "Energy Management", "Lifecycle Optimization"]),
                    ("Direct Air Capture Contactor System for Atmospheric Carbon Removal", "Modular contactor structure passing ambient air over structured solid amine sorbent beds with vacuum regeneration.", ["B01D 53/04", "B01D 53/62"], ["Direct Air Capture", "Carbon Dioxide Removal", "Solid Amine Sorbent"]),
                    ("Bi-Directional Wireless Charging Pad for Electric Vehicles", "Inductive power transfer coil array dynamically tuning resonant frequency during vehicle V2G discharge.", ["H02J 50/12", "B60L 53/12"], ["Wireless Charging", "V2G Bi-Directional", "Inductive Power"]),
                    ("High-Density Carbon Nanotube Ultracapacitor Electrode", "Vertical carbon nanotube forest impregnated with ionic liquid electrolyte yielding high pulse power density.", ["H01G 11/26", "H01G 11/58"], ["Ultracapacitor", "Carbon Nanotube", "Pulse Power"]),
                    ("Offshore Floating Wind Turbine Platform with Active Counter-Ballast", "Semi-submersible steel hull incorporating liquid ballast transfer pumps counteracting wave and wind pitch moments.", ["F03D 13/25", "B63B 35/44"], ["Floating Wind Turbine", "Semi-Submersible", "Active Ballast"]),
                ]
            },
            # 5. Cybersecurity & Cryptography (10 patents)
            {
                "domain": "Cybersecurity & Cryptography",
                "orgs": ["Palo Alto Networks", "IBM Corp.", "Cisco Systems", "Cloudflare Inc.", "Microsoft Corp."],
                "templates": [
                    ("Lattice-Based Post-Quantum Asymmetric Key Exchange System", "Cryptographic key encapsulation mechanism based on Learning With Errors (LWE) resilient to quantum attacks.", ["H04L 9/08", "G06F 21/60"], ["Post-Quantum Crypto", "LWE Cryptography", "Key Encapsulation"]),
                    ("Zero-Trust Continuous User Authentication via Behavioral Biometrics", "Endpoint security agent monitoring keystroke dynamics, mouse trajectory curvature, and touch pressure.", ["G06F 21/32", "H04L 9/32"], ["Zero-Trust Security", "Behavioral Biometrics", "Continuous Authentication"]),
                    ("Hardware-Enforced Confidential Computing Enclave for Cloud Workloads", "Processor security architecture isolating guest memory pages with real-time AES-XTS memory encryption keys.", ["G06F 21/53", "G06F 12/14"], ["Confidential Computing", "Hardware Enclave", "Memory Encryption"]),
                    ("Homomorphic Encryption Hardware Coprocessor for Privacy-Preserving Analytics", "ASIC accelerator processing ciphertext polynomial additions and multiplications without decryption.", ["H04L 9/00", "G06F 7/544"], ["Homomorphic Encryption", "Encrypted Analytics", "Polynomial ASIC"]),
                    ("Autonomous Ransomware Detection via Kernel I/O Entropy Analysis", "File system filter driver intercepting high-entropy file writes and creating transient shadow copy restore points.", ["G06F 21/56", "G06F 11/14"], ["Ransomware Protection", "Entropy Analysis", "Kernel Security Driver"]),
                    ("Decentralized Sovereign Identity Verification using Zero-Knowledge Proofs", "Identity protocol generating zk-SNARK attestations verifying user age and credentials without revealing PII.", ["H04L 9/32", "G06F 21/62"], ["Zero-Knowledge Proof", "zk-SNARK", "Self-Sovereign Identity"]),
                    ("Software-Defined Perimeter (SDP) Controller for Microsegmented Cloud Networks", "Network gateway dynamically opening single-packet authorization (SPA) ports for authenticated clients.", ["H04L 29/06", "H04L 12/46"], ["Software Defined Perimeter", "Single-Packet Auth", "Microsegmentation"]),
                    ("AI-Driven Automated Threat Hunting Engine for Extended Detection and Response", "XDR correlation engine linking endpoint telemetry, DNS queries, and identity logs into incident graphs.", ["G06F 21/55", "G06N 5/04"], ["XDR Security", "Threat Hunting", "Incident Graph"]),
                    ("Secure Multi-Party Computation (SMPC) Protocol for Joint Data Analysis", "Cryptographic protocol enabling separate banking entities to evaluate shared risk metrics without disclosing raw records.", ["H04L 9/08", "G06F 21/62"], ["Multi-Party Computation", "SMPC", "Data Privacy"]),
                    ("Automated Software Bill of Materials (SBOM) Vulnerability Correlation Engine", "Build system parser parsing dependency graphs and cross-referencing CVE repositories to block vulnerable builds.", ["G06F 21/57", "G06F 8/71"], ["SBOM Analysis", "Supply Chain Security", "Vulnerability Scanner"]),
                ]
            },
            # 6. Robotics & Autonomous Systems (10 patents)
            {
                "domain": "Robotics & Autonomous Systems",
                "orgs": ["Boston Dynamics", "Tesla Inc.", "Intuitive Surgical", "FANUC Corp.", "DJI Technology"],
                "templates": [
                    ("Dynamic Quadruped Locomotion Controller for Uneven Rough Terrain", "Model predictive control framework adjusting leg ground reaction forces in real time to recover balance.", ["B62D 57/028", "G05D 1/02"], ["Quadruped Robot", "Locomotion Control", "Model Predictive Control"]),
                    ("High-Fidelity Surgical Robotic Arm with Haptic Force Feedback", "Tele-operated surgical manipulator featuring fiber-Bragg sensor arrays communicating micro-Newton resistance.", ["A61B 34/30", "B25J 13/08"], ["Surgical Robotics", "Haptic Feedback", "Fiber-Bragg Sensors"]),
                    ("Autonomous Aerial Drone Swarm Coordination without Centralized Gateway", "Decentralized mesh networking protocol allowing 100+ drones to execute collaborative search trajectories.", ["G05D 1/10", "H04W 84/18"], ["Drone Swarm", "Mesh Coordination", "Autonomous Aerial"]),
                    ("Compliance-Controlled Soft Robotic End-Effector for Fragile Object Manipulation", "Pneumatically actuated elastomer gripper altering finger stiffness based on tactile optical pressure sensors.", ["B25J 15/12", "B25J 9/14"], ["Soft Robotics", "Elastomer Gripper", "Tactile Optical Sensor"]),
                    ("Simultaneous Localization and Mapping (SLAM) Using Solid-State LiDAR", "Perception pipeline fusing point clouds from non-repetitive solid-state LiDAR sensors for high-speed mapping.", ["G01S 17/89", "G05D 1/02"], ["LiDAR SLAM", "Solid-State LiDAR", "3D Mapping"]),
                    ("Humanoid Robot Bipedal Walking with Whole-Body Inverse Dynamics", "Real-time controller solving momentum conservation equations to enable stable staircase traversal.", ["B62D 57/032", "G05B 19/409"], ["Humanoid Robot", "Bipedal Traversal", "Whole-Body Control"]),
                    ("Collaborative Industrial Robot Arm with Sensorless Contact Detection", "Cobot joint drive monitoring motor current ripple and joint encoder discrepancies to stop instantly upon human impact.", ["B25J 19/06", "F16H 49/00"], ["Collaborative Robot", "Cobot Safety", "Sensorless Detection"]),
                    ("Autonomous Underwater Vehicle (AUV) Acoustic Navigation under Ice Sheets", "Subsea positioning system processing ultra-short baseline acoustic transponder telemetry.", ["G05D 1/06", "B63G 8/00"], ["Autonomous Subsea", "AUV Navigation", "Acoustic Telemetry"]),
                    ("Agricultural Robotic Harvesting System with Multispectral Vision", "Autonomous tractor attachment using multispectral imaging to identify ripe fruit and execute delicate robotic picking.", ["A01D 46/30", "G06T 7/00"], ["Agri-Robotics", "Multispectral Vision", "Robotic Harvesting"]),
                    ("Autonomous Warehouse Mobile Robot Fleet Scheduling Engine", "Centralized fleet management system computing conflict-free topological routes for 500+ AMR units.", ["G06Q 10/08", "G05D 1/02"], ["AMR Fleet", "Warehouse Automation", "Path Scheduling"]),
                ]
            },
            # 7. Semiconductor & Microelectronics (10 patents)
            {
                "domain": "Semiconductors & Microelectronics",
                "orgs": ["TSMC", "Intel Corp.", "ASML", "Applied Materials", "Samsung Electronics"],
                "templates": [
                    ("Gate-All-Around (GAA) RibbonFET Transistor Structure below 2nm Node", "Nanosheet transistor architecture incorporating multi-stack silicon channels separated by inner dielectric spacers.", ["H01L 29/775", "H01L 21/336"], ["GAAFET", "RibbonFET", "Nanosheet Transistor"]),
                    ("Extreme Ultraviolet (EUV) Lithography Scanner with Anamorphic Projection", "Optical illumination system operating at 13.5nm wavelength with 0.55 High-NA mirrors compensating astigmatism.", ["G03F 7/20", "H01L 21/027"], ["EUV Lithography", "High-NA EUV", "Anamorphic Mirror"]),
                    ("3D Heterogeneous Chiplet Packaging with Micro-Bump Interconnects", "Silicon interposer structure bonding memory and compute dies at a 10-micron interconnect pitch.", ["H01L 25/065", "H01L 23/48"], ["3D Packaging", "Chiplet Architecture", "Silicon Interposer"]),
                    ("Backside Power Delivery Network (BSPDN) for Advanced Logic Dies", "Substrate technology routing power lines through buried power rails on the silicon backside.", ["H01L 23/52", "H01L 21/768"], ["Backside Power Delivery", "Buried Power Rail", "BSPDN"]),
                    ("Magnetoresistive Random-Access Memory (MRAM) Cell with Spin-Orbit Torque", "Non-volatile memory element featuring a heavy-metal channel writing magnetic states with sub-nanosecond pulses.", ["H01L 27/22", "G11C 11/16"], ["SOT-MRAM", "Spin-Orbit Torque", "Non-Volatile Memory"]),
                    ("Atomic Layer Deposition (ALD) Process for Ultra-Thin High-k Dielectrics", "Precursor delivery cycle depositing uniform ruthenium-doped hafnium oxide films in 3D trench structures.", ["H01L 21/28", "C23C 16/455"], ["Atomic Layer Deposition", "High-k Dielectric", "Hafnium Oxide"]),
                    ("Gallium Nitride (GaN) High-Electron-Mobility Transistor for Power Electronics", "Semiconductor device grown on silicon substrates featuring AlGaN/GaN heterojunctions handling 1200V breakdowns.", ["H01L 29/778", "H01L 21/338"], ["GaN HEMT", "Power Semiconductor", "Wide-Bandgap"]),
                    ("Phase-Change Memory (PCM) Array for Neuromorphic Computing", "Chalcogenide glass memory cell storing multi-level conductance states to mirror biological synaptic weights.", ["G11C 13/00", "H01L 45/00"], ["Phase-Change Memory", "Neuromorphic Hardware", "Chalcogenide Glass"]),
                    ("Chemical Mechanical Planarization (CMP) Slurry for Cobalt Interconnect Polish", "Abrasive chemical formulation containing organic corrosion inhibitors preserving cobalt wire integrity.", ["H01L 21/321", "C09G 1/02"], ["CMP Slurry", "Cobalt Interconnect", "Planarization"]),
                    ("Direct Bond Interconnect (DBI) Cu-Cu Wafer-to-Wafer Bonding Process", "Surface activation process enabling oxide and copper fusion bonding at room temperature without adhesives.", ["H01L 21/60", "H01L 25/18"], ["Direct Copper Bonding", "Wafer-to-Wafer", "DBI Technology"]),
                ]
            },
            # 8. MedTech & Medical Devices (10 patents)
            {
                "domain": "MedTech & Medical Devices",
                "orgs": ["Medtronic", "Abbott Laboratories", "Boston Scientific", "Siemens Healthineers", "Philips Healthcare"],
                "templates": [
                    ("Continuous Glucose Monitor with Subcutaneous Fluorescence Sensor", "Wearable enzymatic sensor measuring interstitial fluid glucose concentration via optical fluorescence lifetime.", ["A61B 5/145", "A61B 5/00"], ["Continuous Glucose Monitor", "CGM Sensor", "Fluorescence Lifetime"]),
                    ("Transcatheter Aortic Valve Replacement (TAVR) Delivery Catheter", "Self-expanding pericardial heart valve delivery system featuring a deflectable tip for tortuous anatomy.", ["A61F 2/24", "A61M 25/01"], ["TAVR Valve", "Heart Valve Catheter", "Structural Heart"]),
                    ("Deep Brain Stimulation (DBS) Electrode with Independent Contact Control", "Neurostimulation lead incorporating 16 directional micro-electrodes shaping therapeutic electric fields.", ["A61N 1/05", "A61N 1/36"], ["Deep Brain Stimulation", "DBS Neurostimulator", "Directional Lead"]),
                    ("Ultra-Fast 7-Tesla MRI Pulse Sequence for Microvascular Imaging", "Magnetic resonance acquisition scheme accelerating k-space sampling using compressed sensing.", ["G01R 33/56", "A61B 5/055"], ["7T MRI Scanner", "Compressed Sensing", "Microvascular Imaging"]),
                    ("Wearable Cardioverter Defibrillator Garment with Dry Sensor Array", "Sub-vest garment incorporating dry capacitive ECG electrodes sensing ventricular fibrillation without gel.", ["A61N 1/39", "A61B 5/0408"], ["Wearable Defibrillator", "Dry ECG Sensors", "Arrhythmia Protection"]),
                    ("Endoscopic Surgical Stapler with Smart Tissue Thickness Sensing", "Motorized surgical stapler evaluating tissue compression force before firing titanium staples.", ["A61B 17/068", "A61B 17/00"], ["Surgical Stapler", "Tissue Compression", "Endoscopic Surgery"]),
                    ("Artificial Pancreas Closed-Loop Control System with Dual Hormone Infusion", "Automated delivery algorithm dispensing insulin and glucagon based on predictive glucose trends.", ["A61M 5/172", "G16H 20/17"], ["Artificial Pancreas", "Closed-Loop Insulin", "Dual Hormone"]),
                    ("Bioresorbable Vascular Scaffold for Coronary Artery Disease", "Poly-L-lactic acid stent coated with everolimus dissolving completely within 36 months.", ["A61F 2/915", "A61L 31/14"], ["Bioresorbable Stent", "Coronary Scaffold", "Everolimus Eluting"]),
                    ("Intravascular Ultrasound (IVUS) Catheter with Integrated Optical Coherence Tomography", "Dual-modal imaging probe providing simultaneous acoustic cross-sections and optical tissue resolution.", ["A61B 8/12", "A61B 5/00"], ["IVUS Probe", "Dual OCT Ultrasound", "Intravascular Imaging"]),
                    ("Non-Invasive Intracranial Pressure Monitor Using Ocular Sonography", "Ultrasonic device evaluating optic nerve sheath diameter to quantify cerebral spinal fluid pressure.", ["A61B 8/10", "A61B 5/03"], ["Intracranial Pressure", "Ocular Sonography", "Optic Nerve Sheath"]),
                ]
            },
            # 9. Next-Gen Wireless 6G & Communications (10 patents)
            {
                "domain": "Wireless Communications & 6G",
                "orgs": ["Qualcomm Inc.", "Nokia Bell Labs", "Ericsson", "Samsung Electronics", "Huawei Technologies"],
                "templates": [
                    ("Reconfigurable Intelligent Surface (RIS) for Sub-THz 6G Beamforming", "Meta-surface array of tunable liquid crystal phase shifters redirecting 140GHz signals around physical obstacles.", ["H04B 7/06", "H01Q 15/00"], ["Reconfigurable Surface", "Sub-THz 6G", "Metasurface Beamforming"]),
                    ("Joint Communication and Sensing (JCAS) Waveform Design", "OFDM frame structure embedding radar sensing preambles to map environmental surroundings while transmitting data.", ["H04L 27/26", "G01S 7/02"], ["JCAS Sensing", "Integrated Sensing Communication", "6G Waveform"]),
                    ("Terahertz (THz) Transceiver Front-End with Integrated Photonic Mixer", "Radio front-end converting optical laser pulses to 300GHz wireless carrier waves for 100Gbps transmission.", ["H04B 10/00", "H01Q 21/00"], ["Terahertz Wireless", "Photonic Mixer", "100Gbps Link"]),
                    ("Ultra-Dense LEO Satellite Constellation Dynamic Inter-Satellite Link Routing", "Laser communication routing algorithm adapting path choices to orbital movement in low-Earth orbit.", ["H04B 7/185", "H04W 40/20"], ["LEO Constellation", "Laser Inter-Satellite", "Satellite Routing"]),
                    ("Cell-Free Massive MIMO Architecture with Distributed Access Points", "Network architecture eliminating cell boundaries by processing user streams across 64 geographically dispersed APs.", ["H04B 7/0413", "H04W 16/28"], ["Cell-Free MIMO", "Massive MIMO", "Distributed Access Points"]),
                    ("Semantic Communications Framework Using Deep Joint Source-Channel Coding", "Neural transmitter sending low-dimensional semantic feature vectors over noisy wireless channels.", ["H04L 1/00", "G06N 3/08"], ["Semantic Communications", "Joint Source-Channel", "Deep Learning Codec"]),
                    ("Full-Duplex Wireless Transceiver with Multi-Stage Self-Interference Cancellation", "RF circuit combining analog RF cancellation and digital DSP subtraction to enable simultaneous TX/RX on one frequency.", ["H04B 1/525", "H04L 5/14"], ["Full Duplex Wireless", "Self-Interference Cancellation", "Same Frequency TX/RX"]),
                    ("AI-Powered Dynamic Spectrum Sharing in CBRS Bands", "Cloud spectrum controller negotiating radio spectrum allocations between primary radar and secondary commercial tiers.", ["H04W 16/14", "G06N 20/00"], ["Spectrum Sharing", "CBRS Band", "Dynamic Radio Access"]),
                    ("Ambient Backscatter Communication Node Powered by RF Energy Harvesting", "Zero-energy IoT tag reflecting ambient Wi-Fi signals to transmit sensor telemetry without batteries.", ["H04B 1/38", "H02J 50/00"], ["Ambient Backscatter", "Zero-Energy IoT", "RF Harvesting"]),
                    ("Ultra-Reliable Low-Latency Communication (URLLC) Packet Duplication", "Multi-connectivity radio protocol sending redundant data packets simultaneously over 5G NR and Wi-Fi 7.", ["H04W 28/04", "H04L 1/08"], ["URLLC Protocol", "Packet Duplication", "Sub-Millisecond Latency"]),
                ]
            },
            # 10. Autonomous Vehicles & Smart Mobility (8 patents)
            {
                "domain": "Autonomous Vehicles & Mobility",
                "orgs": ["Waymo LLC", "Tesla Inc.", "Cruise LLC", "NVIDIA Corp.", "Baidu Inc."],
                "templates": [
                    ("Multi-Modal Sensor Fusion for Autonomous Vehicle Occlusion Detection", "Perception system combining 4D radar and LiDAR point clouds to detect pedestrian movements behind parked vehicles.", ["G05D 1/02", "G01S 13/86"], ["Sensor Fusion", "Autonomous Occlusion", "4D Radar LiDAR"]),
                    ("Predictive Trajectory Planning for Vulnerable Road Users in Complex Intersections", "Machine learning trajectory engine forecasting bicycle and pedestrian motion 5 seconds into the future.", ["G08G 1/16", "G06N 3/08"], ["Trajectory Planning", "Pedestrian Safety", "Intersection Navigation"]),
                    ("Steer-by-Wire Actuator System with Triple-Redundant Fault Fallback", "Electronic steering system featuring isolated dual-winding brushless motors maintaining steerability during electrical loss.", ["B62D 5/04", "B62D 6/00"], ["Steer-by-Wire", "Triple Redundancy", "Fault Tolerant Steering"]),
                    ("V2X Cooperative Perception Protocol for Blind Spot Collision Warning", "Direct C-V2X communication message sharing real-time vehicle bounding boxes across intersection corners.", ["H04W 4/40", "G08G 1/0967"], ["C-V2X Communication", "Cooperative Perception", "Blind Spot Warning"]),
                    ("Automated Valet Parking Engine via Underground Mapping Beacons", "Vehicle self-parking system navigating underground multi-story garages using ultrawideband (UWB) beacons.", ["G01S 5/02", "G08G 1/14"], ["Automated Valet Parking", "UWB Positioning", "Self-Parking Vehicle"]),
                    ("Thermal Infrared Camera Processing for Nighttime Autonomous Driving", "Deep convolutional model identifying unlit obstacles and wildlife in total darkness beyond headlight range.", ["G06T 7/00", "B60R 11/04"], ["Thermal IR Camera", "Nighttime Perception", "Obstacle Detection"]),
                    ("Dynamic Battery Pre-Conditioning Protocol based on Navigation Route Topology", "EV thermal management system heating battery cells to optimal fast-charging temperatures prior to Supercharger arrival.", ["B60L 58/27", "H01M 10/625"], ["Battery Pre-Conditioning", "EV Fast Charging", "Thermal Management"]),
                    ("Driver State Monitoring via Infrared Photoplethysmography Steering Wheel", "Cabin monitoring system evaluating heart rate variability through steering wheel contact sensors to alert micro-sleep.", ["A61B 5/18", "B60K 28/06"], ["Driver Monitoring", "Heart Rate PPG", "Micro-Sleep Alert"]),
                ]
            }
        ]

        counter = 1000
        records = []
        for cat in domains_and_data:
            domain_name = cat["domain"]
            org_list = cat["orgs"]
            templates = cat["templates"]

            for idx, (title, abstract, ipc_codes, keywords) in enumerate(templates):
                counter += 1
                patent_num = f"US{11500000 + counter}B2" if (counter % 3 != 0) else f"EP{3800000 + counter}A1"
                org = org_list[idx % len(org_list)]
                
                # Inventors
                inv_first = ["Dr. Elena", "Dr. Marcus", "Dr. Wei", "Prof. Aris", "Dr. Sarah", "Dr. Hiroshi", "Dr. Amara", "Dr. David"]
                inv_last = ["Vance", "Chen", "Zhang", "Thorne", "Jenkins", "Tanaka", "Okonkwo", "Miller"]
                inv1 = f"{inv_first[idx % len(inv_first)]} {inv_last[(idx * 2) % len(inv_last)]}"
                inv2 = f"{inv_first[(idx + 3) % len(inv_first)]} {inv_last[(idx + 1) % len(inv_last)]}"
                inventors = [inv1, inv2]

                year = 2018 + (counter % 8)  # 2018 to 2025
                month = f"{(counter % 12) + 1:02d}"
                day = f"{(counter % 28) + 1:02d}"
                filing_date = f"{year - 2}-{month}-{day}"
                pub_date = f"{year}-{month}-{day}"

                st = "Granted" if (counter % 4 != 0) else ("Pending" if counter % 4 == 0 else "Expired")
                claims = 10 + (counter % 35)
                citations = 5 + ((counter * 7) % 240)

                rec = PatentRecord(
                    patent_number=patent_num,
                    title=title,
                    abstract=abstract,
                    assignee_organization=org,
                    inventors=inventors,
                    technology_domain=domain_name,
                    ipc_codes=ipc_codes,
                    cpc_codes=[f"CPC-{code.replace(' ', '')}" for code in ipc_codes],
                    filing_date=filing_date,
                    publication_date=pub_date,
                    publication_year=year,
                    status=st,
                    claims_count=claims,
                    citations_count=citations,
                    url=f"https://patents.google.com/patent/{patent_num}/en",
                    keywords=keywords,
                    source_api="local_seed",
                    external_id=patent_num,
                )
                records.append(rec)

        db.add_all(records)

        # Also seed PatentTrends
        trends_data = [
            PatentTrend(
                technology_domain="Artificial Intelligence & Machine Learning",
                growth_rate=44.8,
                patent_count=12450,
                top_assignees=["Google LLC", "IBM Corp.", "Microsoft Corp.", "NVIDIA Corp."],
                key_keywords=["Generative AI", "Transformers", "LLMs", "Neural Hardware"],
                is_emerging=True,
                summary="Accelerating multi-modal generative models and specialized tensor processing ASIC architectures.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Quantum Computing & Information",
                growth_rate=38.2,
                patent_count=4120,
                top_assignees=["IBM Corp.", "Google LLC", "Intel Corp.", "Rigetti Computing"],
                key_keywords=["Surface Codes", "Cryo-CMOS", "Trapped Ion", "QKD"],
                is_emerging=True,
                summary="Rapid expansion in fault-tolerant surface codes and cryogenic CMOS qubit control circuits.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Biotechnology & Genomics",
                growth_rate=32.6,
                patent_count=8900,
                top_assignees=["Broad Institute", "Pfizer Inc.", "Moderna TX", "Genentech"],
                key_keywords=["CRISPR Base Editing", "Lipid Nanoparticles", "CAR-T", "Prime Editing"],
                is_emerging=False,
                summary="Strong focus on precision gene editing tools, mRNA lipid nanoparticles, and spatial transcriptomics.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Clean Energy & Storage",
                growth_rate=29.4,
                patent_count=9800,
                top_assignees=["Tesla Inc.", "Siemens AG", "CATL", "Panasonic Corp."],
                key_keywords=["Solid-State Batteries", "Perovskite Tandem", "Green Hydrogen", "Direct Air Capture"],
                is_emerging=False,
                summary="Surge in solid-state lithium electrolytes, sodium-ion grid storage, and direct atmospheric carbon capture.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Cybersecurity & Cryptography",
                growth_rate=35.1,
                patent_count=6700,
                top_assignees=["Palo Alto Networks", "IBM Corp.", "Cisco Systems", "Cloudflare"],
                key_keywords=["Post-Quantum Crypto", "Zero-Trust", "Confidential Computing", "zk-SNARKs"],
                is_emerging=True,
                summary="Standardization of post-quantum lattice cryptography and hardware-enforced confidential enclaves.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Semiconductors & Microelectronics",
                growth_rate=27.5,
                patent_count=15300,
                top_assignees=["TSMC", "Intel Corp.", "ASML", "Applied Materials", "Samsung"],
                key_keywords=["GAAFET", "High-NA EUV", "3D Chiplets", "Backside Power"],
                is_emerging=False,
                summary="Transition to 2nm Gate-All-Around nanosheets and High-NA EUV lithography optics.",
                year=2024,
            ),
            PatentTrend(
                technology_domain="Wireless Communications & 6G",
                growth_rate=41.0,
                patent_count=5200,
                top_assignees=["Qualcomm Inc.", "Nokia Bell Labs", "Ericsson", "Samsung"],
                key_keywords=["Reconfigurable Surfaces", "Sub-THz 6G", "JCAS Sensing", "Cell-Free MIMO"],
                is_emerging=True,
                summary="Pioneering sub-THz frequencies, integrated sensing-communication waveforms, and cell-free massive MIMO.",
                year=2024,
            ),
        ]
        db.add_all(trends_data)

        await db.commit()
        logger.info(f"Successfully seeded {len(records)} patent records and {len(trends_data)} patent trends!")
