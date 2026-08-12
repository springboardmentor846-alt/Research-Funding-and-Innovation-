"""
Database Seeding Script for Research Funding & Innovation Intelligence Platform
Populates database with mock data across users, profiles, funding grants, research publications, trends, patents, technologies, evaluations, and notifications.
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Append backend path to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.db.session import async_engine, AsyncSessionLocal
from app.db.base_class import Base
from app.models import (
    User, ResearchProfile, FundingOpportunity, SavedGrant,
    Publication, ResearchTrend, Patent, Technology,
    InnovationEvaluation, Notification
)
from app.core.constants import UserRole
from app.core.security import get_password_hash


async def seed_data():
    print("🚀 Initializing Database Tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully.")

    async with AsyncSessionLocal() as session:
        print("🌱 Seeding Demo Users across 4 roles...")
        password_hash = get_password_hash("Password123!")

        user_researcher = User(
            email="researcher@example.com",
            hashed_password=password_hash,
            full_name="Dr. Aris Thorne",
            role=UserRole.RESEARCHER,
            is_active=True,
            is_verified=True
        )
        user_startup = User(
            email="startup@example.com",
            hashed_password=password_hash,
            full_name="Elena Vance",
            role=UserRole.STARTUP_FOUNDER,
            is_active=True,
            is_verified=True
        )
        user_manager = User(
            email="manager@example.com",
            hashed_password=password_hash,
            full_name="Marcus Brody",
            role=UserRole.INNOVATION_MANAGER,
            is_active=True,
            is_verified=True
        )
        user_admin = User(
            email="admin@example.com",
            hashed_password=password_hash,
            full_name="System Administrator",
            role=UserRole.SYSTEM_ADMIN,
            is_active=True,
            is_verified=True
        )

        session.add_all([user_researcher, user_startup, user_manager, user_admin])
        await session.commit()
        await session.refresh(user_researcher)
        await session.refresh(user_startup)

        # Seed Research Profile
        profile = ResearchProfile(
            user_id=user_researcher.id,
            organization="Stanford Institute for AI & Robotics",
            department="Computer Science & Neuro-Engineering",
            academic_title="Associate Professor",
            bio="Lead researcher pioneering neuromorphic algorithms, quantum machine learning, and scalable autonomous robotics.",
            research_domains=["Artificial Intelligence", "Quantum Computing", "Robotics"],
            keywords=["Neural Networks", "Neuromorphic Chips", "Quantum ML", "Graph Neural Networks"],
            technology_areas=["Deep Learning", "Quantum Hardware", "Autonomous Systems"],
            total_publications=18,
            total_citations=840,
            h_index=14,
            i10_index=16
        )
        session.add(profile)

        print("🌱 Seeding Funding Opportunities...")
        grants = [
            FundingOpportunity(
                title="NSF AI & Quantum Information Systems Convergence Grant",
                agency="National Science Foundation (NSF)",
                opportunity_type="Government Grants",
                description="Supports fundamental research breakthroughs at the intersection of artificial intelligence architectures and quantum computing systems.",
                total_funding_amount=5000000.0,
                min_award=500000.0,
                max_award=1500000.0,
                currency="USD",
                deadline=datetime.utcnow() + timedelta(days=45),
                application_url="https://nsf.gov/grants/ai-quantum-2026",
                status="OPEN",
                eligibility_criteria=["Must be US accredited research university or non-profit institute", "PI must hold PhD in CS or Physics"],
                target_domains=["Artificial Intelligence", "Quantum Computing"],
                target_keywords=["Quantum ML", "Neuromorphic Chips", "Neural Networks"],
                eligible_applicant_types=["Researcher", "University"]
            ),
            FundingOpportunity(
                title="Horizon Europe DeepTech Breakthrough Catalyst Call",
                agency="European Innovation Council (EIC)",
                opportunity_type="International Funding Agencies",
                description="Accelerator grant and equity funding for high-risk, high-impact deeptech ventures scaling novel hardware and AI solutions.",
                total_funding_amount=12000000.0,
                min_award=1000000.0,
                max_award=2500000.0,
                currency="EUR",
                deadline=datetime.utcnow() + timedelta(days=90),
                application_url="https://eic.ec.europa.eu/calls/deeptech-2026",
                status="OPEN",
                eligibility_criteria=["EU or Associated Country SME/Startup", "TRL 4-7 technology readiness"],
                target_domains=["Clean Energy", "Artificial Intelligence", "Biotechnology"],
                target_keywords=["Deep Learning", "Battery Tech", "Genomics"],
                eligible_applicant_types=["Startup Founder", "Small Business"]
            ),
            FundingOpportunity(
                title="ARPA-E Next-Gen Solid-State Battery Commercialization Fund",
                agency="Advanced Research Projects Agency-Energy (ARPA-E)",
                opportunity_type="Research Councils",
                description="Funding for transformative energy technologies that demonstrate viable pathways to high energy density solid-state lithium metal batteries.",
                total_funding_amount=8000000.0,
                min_award=750000.0,
                max_award=2000000.0,
                currency="USD",
                deadline=datetime.utcnow() + timedelta(days=20),
                application_url="https://arpa-e.energy.gov/funding/ssb-2026",
                status="CLOSING_SOON",
                eligibility_criteria=["US Entities, National Labs, or Consortia"],
                target_domains=["Clean Energy", "Materials Science"],
                target_keywords=["Solid-State Battery", "Lithium Metal", "Energy Density"],
                eligible_applicant_types=["Researcher", "Startup Founder"]
            ),
            FundingOpportunity(
                title="Y Combinator Bio & Deep Tech Seed Accelerator (Fall 2026)",
                agency="Y Combinator",
                opportunity_type="Startup Accelerators",
                description="$500,000 uncapped seed funding plus 3 months intensive pitch preparation for early-stage science and engineering founders.",
                total_funding_amount=500000.0,
                min_award=500000.0,
                max_award=500000.0,
                currency="USD",
                deadline=datetime.utcnow() + timedelta(days=60),
                application_url="https://ycombinator.com/apply",
                status="OPEN",
                eligibility_criteria=["Incorporated startup or founding team with working prototype"],
                target_domains=["Artificial Intelligence", "Biotechnology", "Robotics"],
                target_keywords=["SaaS", "Deep Tech", "Gen AI", "Synthetic Bio"],
                eligible_applicant_types=["Startup Founder"]
            ),
            FundingOpportunity(
                title="NIH Genomic Medicine & Precision Therapeutics Grant",
                agency="National Institutes of Health (NIH)",
                opportunity_type="Government Grants",
                description="R01 grant call for targeted mRNA therapeutics, CRISPR gene editing, and bio-AI modeling tools.",
                total_funding_amount=6500000.0,
                min_award=400000.0,
                max_award=1200000.0,
                currency="USD",
                deadline=datetime.utcnow() + timedelta(days=110),
                application_url="https://nih.gov/grants/r01-genomics",
                status="OPEN",
                eligibility_criteria=["Higher Education & Medical Research Institutions"],
                target_domains=["Biotechnology", "Healthcare"],
                target_keywords=["mRNA", "CRISPR", "Genomics", "Bio-AI"],
                eligible_applicant_types=["Researcher"]
            )
        ]
        session.add_all(grants)
        await session.commit()

        print("🌱 Seeding Research Publications & Emerging Topic Trends...")
        pubs = [
            Publication(
                title="Scalable Neuromorphic Computing via Spike-Timing-Dependent Plasticity",
                authors=["Dr. Aris Thorne", "Dr. Sophia Lin", "Prof. Hans Mueller"],
                journal_or_venue="Nature Electronics",
                publication_year=2025,
                abstract="We demonstrate a 128-core neuromorphic processor leveraging memristive crossbar arrays to achieve 100x lower energy consumption in edge AI inference tasks.",
                citation_count=142,
                doi="10.1038/s41928-025-00123-x",
                paper_url="https://nature.com/articles/s41928-025-00123-x",
                domains=["Artificial Intelligence", "Hardware Architecture"],
                keywords=["Neuromorphic Chips", "Memristors", "Spiking Neural Networks"],
                source_database="OpenAlex"
            ),
            Publication(
                title="Quantum Graph Neural Networks for Molecular Structure Prediction",
                authors=["Dr. Aris Thorne", "Elena Vance"],
                journal_or_venue="IEEE Transactions on Neural Networks and Learning Systems",
                publication_year=2025,
                abstract="Formulates a hybrid quantum-classical graph neural network architecture that significantly accelerates molecular binding affinity prediction for drug discovery.",
                citation_count=89,
                doi="10.1109/TNNLS.2025.9876543",
                paper_url="https://ieeexplore.ieee.org/document/9876543",
                domains=["Quantum Computing", "Artificial Intelligence", "Biotechnology"],
                keywords=["Quantum ML", "Graph Neural Networks", "Drug Discovery"],
                source_database="CrossRef"
            ),
            Publication(
                title="High-Conductivity Solid Electrolytes for Fast-Charging Batteries",
                authors=["Dr. Marcus Chen", "Dr. Sarah Jenkins"],
                journal_or_venue="Science Energy",
                publication_year=2024,
                abstract="Presents a sulfide-based solid-state electrolyte exhibiting room-temperature ionic conductivity superior to liquid organic electrolytes.",
                citation_count=215,
                doi="10.1126/scienergy.2024.55432",
                domains=["Clean Energy", "Materials Science"],
                keywords=["Solid-State Battery", "Lithium Metal", "Electrolytes"],
                source_database="Semantic Scholar"
            )
        ]
        session.add_all(pubs)

        trends = [
            ResearchTrend(
                topic_name="Neuromorphic Edge AI",
                domain="Artificial Intelligence",
                growth_rate_pct=148.5,
                publication_count=1240,
                citation_velocity=28.4,
                hotspot_score=94.2,
                maturity_stage="Emerging",
                yearly_volume_series={"2022": 180, "2023": 340, "2024": 650, "2025": 1240},
                key_keywords=["Spiking Neural Networks", "Memristors", "Edge AI", "Low-Power Chips"]
            ),
            ResearchTrend(
                topic_name="Quantum Graph Neural Networks",
                domain="Quantum Computing",
                growth_rate_pct=185.2,
                publication_count=620,
                citation_velocity=32.1,
                hotspot_score=91.8,
                maturity_stage="Emerging",
                yearly_volume_series={"2022": 45, "2023": 110, "2024": 280, "2025": 620},
                key_keywords=["QNN", "Graph Embeddings", "Variational Quantum Algorithms"]
            ),
            ResearchTrend(
                topic_name="Solid-State Lithium Metal Batteries",
                domain="Clean Energy",
                growth_rate_pct=76.4,
                publication_count=3100,
                citation_velocity=45.0,
                hotspot_score=86.5,
                maturity_stage="Growing",
                yearly_volume_series={"2022": 950, "2023": 1450, "2024": 2200, "2025": 3100},
                key_keywords=["Solid Electrolytes", "Dendrite Suppression", "Energy Density"]
            ),
            ResearchTrend(
                topic_name="Targeted mRNA Nanoparticle Delivery",
                domain="Biotechnology",
                growth_rate_pct=62.0,
                publication_count=4200,
                citation_velocity=52.3,
                hotspot_score=84.0,
                maturity_stage="Mature",
                yearly_volume_series={"2022": 1800, "2023": 2600, "2024": 3400, "2025": 4200},
                key_keywords=["LNP Delivery", "CRISPR Editing", "Oncology mRNA"]
            )
        ]
        session.add_all(trends)

        print("🌱 Seeding Patents & IPC Landscape...")
        patents = [
            Patent(
                patent_number="US-11894562-B2",
                title="Neuromorphic Crossbar Circuit Architecture with On-Chip Spike Training",
                assignee="Stanford University / Neuromorphic Tech Inc",
                filing_date=datetime(2023, 5, 14),
                grant_date=datetime(2024, 2, 20),
                ipc_classification="G06N 3/063",
                technology_domain="Artificial Intelligence",
                citation_count=48,
                abstract="A neuromorphic hardware accelerator comprising non-volatile memory arrays configured for real-time backpropagation through time (BPTT).",
                claims_summary="1. A hardware accelerator comprising memristive cells... 2. The circuit of claim 1 wherein spike timing dictates weight adjustment...",
                cluster_id="CLUSTER_AI_HARDWARE",
                patent_url="https://patents.google.com/patent/US11894562B2",
                keywords=["Neuromorphic", "Memristor", "Crossbar Array", "On-chip Learning"]
            ),
            Patent(
                patent_number="US-11985431-B1",
                title="Method for Quantum Circuit Compilation using Graph Embeddings",
                assignee="Google LLC / Quantum AI Lab",
                filing_date=datetime(2023, 9, 10),
                grant_date=datetime(2024, 6, 12),
                ipc_classification="G06N 10/00",
                technology_domain="Quantum Computing",
                citation_count=35,
                abstract="Compiles high-level quantum algorithms into fault-tolerant native gate pulses using graph neural network cost function optimization.",
                claims_summary="1. A computer-implemented method for quantum gate optimization...",
                cluster_id="CLUSTER_QUANTUM_COMPILATION",
                patent_url="https://patents.google.com/patent/US11985431B1",
                keywords=["Quantum Computing", "Compiler", "Graph Neural Network", "Qubit Control"]
            ),
            Patent(
                patent_number="US-11756402-B2",
                title="Sulfide Solid Electrolyte Layer with Integrated Interfacial Polymer Barrier",
                assignee="Siemens Energy AG / QuantumScape Corp",
                filing_date=datetime(2022, 11, 4),
                grant_date=datetime(2023, 9, 19),
                ipc_classification="H01M 10/0562",
                technology_domain="Clean Energy",
                citation_count=62,
                abstract="Discloses a composite solid battery separator layer designed to prevent lithium dendrite growth across 1000+ charge cycles.",
                claims_summary="1. A solid-state energy storage unit comprising a protective polymer composite...",
                cluster_id="CLUSTER_BATTERY_TECH",
                patent_url="https://patents.google.com/patent/US11756402B2",
                keywords=["Solid-State Battery", "Electrolyte", "Dendrite Barrier"]
            )
        ]
        session.add_all(patents)

        print("🌱 Seeding Technologies (TRL Tracking)...")
        technologies = [
            Technology(
                name="Neuromorphic Edge AI Chips",
                domain="Artificial Intelligence",
                description="Brain-inspired analog computing hardware delivering extreme energy efficiency for edge processing.",
                trl_level=6,
                adoption_stage="Pilot",
                market_readiness_score=78.5,
                competitive_density="High",
                key_innovators=["Stanford", "Intel Labs", "SynSense", "BrainChip"],
                patent_count=340,
                funding_volume=450000000.0
            ),
            Technology(
                name="Quantum Machine Learning (QML) Algorithms",
                domain="Quantum Computing",
                description="Hybrid variational quantum circuits for high-dimensional drug discovery & optimization problems.",
                trl_level=4,
                adoption_stage="R&D",
                market_readiness_score=52.0,
                competitive_density="Medium",
                key_innovators=["Google Quantum AI", "IBM Quantum", "Rigetti", "Xanadu"],
                patent_count=120,
                funding_volume=280000000.0
            ),
            Technology(
                name="Solid-State Lithium Metal Batteries",
                domain="Clean Energy",
                description="Next-generation battery technology substituting liquid electrolytes with solid ceramics/polymers for 2x energy density.",
                trl_level=7,
                adoption_stage="Commercial",
                market_readiness_score=84.2,
                competitive_density="High",
                key_innovators=["QuantumScape", "Solid Power", "Toyota", "Samsung SDI"],
                patent_count=1850,
                funding_volume=3200000000.0
            )
        ]
        session.add_all(technologies)

        print("🌱 Seeding Sample Innovation Evaluations & Notifications...")
        eval_sample = InnovationEvaluation(
            user_id=user_researcher.id,
            project_title="Neuromorphic Edge AI Processor for Autonomous Drones",
            domain="Artificial Intelligence",
            description="Developing ultra-low power spiking neural network chip capable of onboard flight obstacle avoidance at sub-watt power budgets.",
            research_novelty_score=92.0,
            patent_strength_score=85.0,
            tech_maturity_score=70.0,
            market_potential_score=88.0,
            funding_relevance_score=90.0,
            total_innovation_score=86.3, # Calculated weighted
            productization_recommendations=[
                "Prepare direct MVP commercial roll-out in Artificial Intelligence.",
                "Initiate pilot customer deployments with corporate drone innovation partners."
            ],
            licensing_opportunities=[
                "Execute non-exclusive licensing agreements with tier-1 enterprise leaders.",
                "Structure milestone-based royalty model (4-6% net sales)."
            ],
            startup_creation_recommendations=[
                "Incorporate a university spin-out or deep-tech startup entity.",
                "Target Y Combinator, NSF I-Corps, or specialized deep-tech accelerators."
            ],
            industry_partnership_suggestions=[
                "Form joint development agreement (JDA) with commercial drone makers."
            ]
        )
        session.add(eval_sample)

        notifications = [
            Notification(
                user_id=user_researcher.id,
                title="New Grant Match: NSF AI & Quantum Systems",
                message="Your research profile matches the NSF AI & Quantum Information Systems Convergence Grant with a 92.5% eligibility match score.",
                category="funding",
                is_read=False
            ),
            Notification(
                user_id=user_researcher.id,
                title="Patent Citation Alert: US-11894562-B2",
                message="Your patent US-11894562-B2 was cited by Google Quantum AI Lab in a new filing.",
                category="patent",
                is_read=False
            ),
            Notification(
                user_id=user_researcher.id,
                title="Trend Surge: Neuromorphic Edge AI (+148% Growth)",
                message="Neuromorphic Edge AI topic publication velocity increased by 148.5% YoY in Nature & IEEE journals.",
                category="trend",
                is_read=True
            )
        ]
        session.add_all(notifications)

        await session.commit()
        print("🎉 Database successfully seeded with rich mock dataset!")


if __name__ == "__main__":
    asyncio.run(seed_data())
