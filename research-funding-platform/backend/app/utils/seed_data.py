import logging
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.core.database import engine, Base
from app.models.models import (
    User, ResearchProfile, FundingOpportunity, Publication,
    Patent, TechTrend, InnovationScore, CommercializationOpportunity, Notification
)

logger = logging.getLogger(__name__)

def seed_all_sample_data(db: Session, force: bool = False):
    try:
        # Guarantee all database tables exist
        Base.metadata.create_all(bind=engine)

        # Check if users already exist
        if not force and db.query(User).count() > 0:
            return {"message": "Database already seeded."}

        if force:
            db.query(Notification).delete()
            db.query(CommercializationOpportunity).delete()
            db.query(InnovationScore).delete()
            db.query(TechTrend).delete()
            db.query(Patent).delete()
            db.query(Publication).delete()
            db.query(FundingOpportunity).delete()
            db.query(ResearchProfile).delete()
            db.query(User).delete()
            db.commit()

        default_pwd = get_password_hash("Password123!")

        # 1. Users
        users_data = [
            {"email": "admin@platform.ai", "full_name": "Dr. Sarah Jenkins", "role": "Administrator", "org": "Global Innovation Institute"},
            {"email": "researcher@university.edu", "full_name": "Prof. Alex Rivera", "role": "Researcher", "org": "MIT AI Lab"},
            {"email": "startup@techventures.io", "full_name": "Elena Rostova", "role": "Startup Founder", "org": "Quantum Dynamics Corp"},
            {"email": "manager@innovation.gov", "full_name": "Marcus Vance", "role": "Innovation Manager", "org": "National Science Foundation"},
            {"email": "biotech.lead@genomics.org", "full_name": "Dr. David Kim", "role": "Researcher", "org": "Broad Institute"},
            {"email": "clean.tech@energyminds.com", "full_name": "Aria Chen", "role": "Startup Founder", "org": "Solaria Tech"},
            {"email": "quantum.research@stanford.edu", "full_name": "Prof. Robert Thorne", "role": "Researcher", "org": "Stanford Physics Lab"},
            {"email": "enterprise@corp.com", "full_name": "Samantha Wright", "role": "Innovation Manager", "org": "Intel AI Research"},
            {"email": "grant.admin@horizon.eu", "full_name": "Jean-Luc Picard", "role": "Administrator", "org": "EU Research Council"},
            {"email": "fellow@ai-align.org", "full_name": "Michael Zhang", "role": "Researcher", "org": "DeepMind Partner Lab"}
        ]

        db_users = []
        for u in users_data:
            user = User(
                email=u["email"],
                hashed_password=default_pwd,
                full_name=u["full_name"],
                role=u["role"],
                organization=u["org"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.flush()
            db_users.append(user)

            # Profile
            profile = ResearchProfile(
                user_id=user.id,
                organization=user.organization,
                domains="Artificial Intelligence, Quantum Computing, Biotechnology",
                keywords="Deep Learning, Neural Networks, Gene Editing, Solar Energy",
                bio=f"Senior specialist at {user.organization} with extensive experience in translational science.",
                publications_count=18,
                patents_count=4,
                h_index=14
            )
            db.add(profile)

        # 2. Funding Opportunities
        funding_data = [
            {
                "title": "ARPA-H Healthcare AI Breakthrough Grant 2026",
                "agency": "Advanced Research Projects Agency for Health",
                "grant_type": "Government",
                "amount": 2500000.0,
                "deadline": "2026-11-15",
                "description": "Multi-million dollar funding for disruptive AI diagnostic models targeting early-stage pancreatic and lung cancer detection.",
                "eligibility_criteria": "Universities, Non-profit Research Labs, Biotech Startups with clinical trial protocols.",
                "keywords": "AI, Oncology, Diagnostics, Machine Learning, Clinical Trials",
                "url": "https://arpa-h.gov/engage-and-connect/opportunities"
            },
            {
                "title": "NSF SBIR Phase II: Deep Tech & Quantum Hardware",
                "agency": "National Science Foundation",
                "grant_type": "Startup Grant",
                "amount": 1000000.0,
                "deadline": "2026-09-30",
                "description": "Commercialization funding for small businesses building fault-tolerant superconducting qubits and room-temperature photonics.",
                "eligibility_criteria": "US Small Businesses (<500 employees) with successful Phase I prototype validation.",
                "keywords": "Quantum Computing, Photonic Chips, Superconducting Qubits, Deep Tech",
                "url": "https://seedfund.nsf.gov/"
            },
            {
                "title": "Horizon Europe Next-Gen Clean Hydrogen & Fusion",
                "agency": "European Innovation Council",
                "grant_type": "International",
                "amount": 4200000.0,
                "deadline": "2026-12-01",
                "description": "Consortium funding for clean hydrogen electrolysis and magnetic confinement fusion energy systems.",
                "eligibility_criteria": "EU and international academic-industry consortiums.",
                "keywords": "Clean Energy, Hydrogen Fuel Cells, Fusion Energy, Decarbonization",
                "url": "https://eic.ec.europa.eu/"
            },
            {
                "title": "NIH Director's Transformative Research Award",
                "agency": "National Institutes of Health",
                "grant_type": "Research Council",
                "amount": 1800000.0,
                "deadline": "2026-10-20",
                "description": "High-risk, high-reward research funding for fundamental synthetic biology and CRISPR gene drive technologies.",
                "eligibility_criteria": "Tenured faculty, Principal Investigators, Senior Scientists.",
                "keywords": "Genomics, Synthetic Biology, CRISPR, Gene Therapy",
                "url": "https://commonfund.nih.gov/"
            },
            {
                "title": "DOE Advanced Grid Resilience & Battery Storage Grant",
                "agency": "Department of Energy",
                "grant_type": "Innovation",
                "amount": 3500000.0,
                "deadline": "2026-08-30",
                "description": "Support for next-generation solid-state lithium battery chemistries and smart grid AI optimization.",
                "eligibility_criteria": "National Labs, Energy Startups, University Engineering Departments.",
                "keywords": "Battery Energy Storage, Solid State Batteries, Smart Grid, AI Infrastructure",
                "url": "https://www.energy.gov/"
            },
            {
                "title": "DARPA Defense Sciences Office (DSO) Open Office Call",
                "agency": "Defense Advanced Research Projects Agency",
                "grant_type": "Government",
                "amount": 5000000.0,
                "deadline": "2026-10-15",
                "description": "High-risk, high-impact research proposals in physics, math, materials, biology, and social sciences.",
                "eligibility_criteria": "All entities, including universities, small businesses, and large defense contractors.",
                "keywords": "Applied Physics, Advanced Materials, Biotechnology, Math, Engineering",
                "url": "https://www.darpa.mil/about-us/offices/dso"
            },
            {
                "title": "Bill & Melinda Gates Foundation Grand Challenges Grant",
                "agency": "Gates Foundation",
                "grant_type": "International",
                "amount": 1500000.0,
                "deadline": "2026-11-30",
                "description": "Global health innovation grants aimed at creating low-cost diagnostics and therapeutics for infectious diseases.",
                "eligibility_criteria": "Academic institutions, non-profit organizations, and commercial startups globally.",
                "keywords": "Global Health, Infectious Disease, Low-Cost Diagnostics, Therapeutics",
                "url": "https://gcgh.grandchallenges.org/"
            },
            {
                "title": "Wellcome Trust Discovery Research Awards",
                "agency": "Wellcome Trust",
                "grant_type": "International",
                "amount": 2800000.0,
                "deadline": "2026-09-15",
                "description": "Funding for bold and creative researchers looking to solve complex health challenges globally.",
                "eligibility_criteria": "Established researchers, research consortiums, and universities.",
                "keywords": "Biomedical, Health Sciences, Clinical Research, Mental Health",
                "url": "https://wellcome.org/grant-funding"
            },
            {
                "title": "Alfred P. Sloan Foundation Scientific Research Fellowship",
                "agency": "Sloan Foundation",
                "grant_type": "Research Council",
                "amount": 75000.0,
                "deadline": "2026-09-15",
                "description": "Prestigious fellowship award for early-career scientists demonstrating outstanding research potential in chemistry, computer science, and economics.",
                "eligibility_criteria": "Early-career faculty and tenure-track researchers.",
                "keywords": "Computer Science, Mathematics, Chemistry, Neuroscience, Economics",
                "url": "https://sloan.org/programs/research"
            },
            {
                "title": "EIC Accelerator Startup DeepTech ScaleUp Funding",
                "agency": "European Innovation Council",
                "grant_type": "Startup Grant",
                "amount": 2500000.0,
                "deadline": "2026-10-08",
                "description": "EIC Accelerator provides funding and equity investment for high-growth deep tech startups in Europe.",
                "eligibility_criteria": "SMEs and startups based in EU member states or associated countries.",
                "keywords": "Deep Tech, Startup Scaleup, Equity Investment, European Innovation",
                "url": "https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator_en"
            },
            {
                "title": "NSF Cyber-Physical Systems (CPS) Breakthrough Research",
                "agency": "National Science Foundation",
                "grant_type": "Government",
                "amount": 1200000.0,
                "deadline": "2026-12-15",
                "description": "Research proposals targeting smart grid networks, autonomous transit, and medical robotics integration.",
                "eligibility_criteria": "Universities, research institutes, and educational organizations.",
                "keywords": "Smart Grid, Cyber-Physical Systems, Medical Robotics, Autonomous Transit",
                "url": "https://www.nsf.gov/funding/"
            },
            {
                "title": "NIH Bio-informatics and Big Data Science Grant",
                "agency": "National Institutes of Health",
                "grant_type": "Research Council",
                "amount": 950000.0,
                "deadline": "2026-08-31",
                "description": "Funding for developing advanced bio-informatics software tools and cloud computing pipelines for genomics.",
                "eligibility_criteria": "Academic labs, medical research institutes, and data science teams.",
                "keywords": "Genomics, Big Data, Bio-informatics, Cloud Pipelines, Software Tools",
                "url": "https://datascience.nih.gov/"
            }
        ]

        for f in funding_data:
            db.add(FundingOpportunity(**f))

        # 3. Publications
        publications_data = [
            {
                "title": "Generative Diffusion Models for De Novo Molecular Design in Oncology",
                "authors": "Alex Rivera, David Kim, Sarah Jenkins",
                "journal": "Nature Machine Intelligence",
                "publication_date": "2026-03-14",
                "citations_count": 142,
                "impact_factor": 18.8,
                "abstract": "We present a 3D equivariant diffusion framework that accelerates target-bound ligand synthesis by 100x while maintaining sub-angstrom binding precision.",
                "keywords": "Artificial Intelligence, Drug Discovery, Generative Models, Cheminformatics",
                "doi": "10.1038/s42256-026-00412-x"
            },
            {
                "title": "Room-Temperature Coherence in Silicon Carbide Quantum Microprocessors",
                "authors": "Robert Thorne, Elena Rostova",
                "journal": "Science Quantum",
                "publication_date": "2026-01-22",
                "citations_count": 89,
                "impact_factor": 24.1,
                "abstract": "Demonstrating 1.2 millisecond spin coherence times in solid-state color centers at ambient temperatures for scalable quantum computing networks.",
                "keywords": "Quantum Computing, Silicon Carbide, Qubits, Solid State Physics",
                "doi": "10.1126/science.abq9801"
            },
            {
                "title": "Perovskite-Silicon Tandem Solar Cells Achieving 34.2% Operational Efficiency",
                "authors": "Aria Chen, Michael Zhang",
                "journal": "Advanced Energy Materials",
                "publication_date": "2025-11-05",
                "citations_count": 210,
                "impact_factor": 29.4,
                "abstract": "Optimized passivating contact layers drastically reduce non-radiative recombination losses in large-area commercial solar panel architectures.",
                "keywords": "Renewable Energy, Photovoltaics, Perovskite, Clean Tech",
                "doi": "10.1002/aenm.202503912"
            }
        ]

        for p in publications_data:
            db.add(Publication(**p))

        # 4. Patents
        patents_data = [
            {
                "patent_number": "US-11984201-B2",
                "title": "Neural Network Architecture for Real-Time Autonomous Robotics Control",
                "assignee": "MIT AI Lab",
                "filing_date": "2024-04-12",
                "grant_date": "2025-09-18",
                "status": "Active",
                "claims_count": 24,
                "abstract": "Method and system for low-latency spatio-temporal path planning using localized edge-computing TPU inference.",
                "tech_field": "Robotics & AI"
            },
            {
                "patent_number": "US-12048110-B1",
                "title": "Superconducting Josephson Junction Array for Error-Corrected Qubit Architectures",
                "assignee": "Quantum Dynamics Corp",
                "filing_date": "2024-08-30",
                "grant_date": "2026-02-10",
                "status": "Active",
                "claims_count": 18,
                "abstract": "Cryogenic microwave resonator filtering system for mitigating thermal flux noise in multi-qubit registers.",
                "tech_field": "Quantum Hardware"
            },
            {
                "patent_number": "EP-3918231-A1",
                "title": "CRISPR-Cas14 Ribonucleoprotein Complexes for Targeted Cell Therapy",
                "assignee": "Broad Institute",
                "filing_date": "2025-02-14",
                "grant_date": None,
                "status": "Pending",
                "claims_count": 32,
                "abstract": "Novel compact nuclease constructs enabling high-fidelity genome editing without off-target double-stranded breaks.",
                "tech_field": "Biotechnology"
            },
            {
                "patent_number": "US-12154302-B2",
                "title": "Solid-State Sodium-Sulfur Battery Membrane Design",
                "assignee": "Solaria Tech",
                "filing_date": "2025-05-18",
                "grant_date": "2026-01-05",
                "status": "Active",
                "claims_count": 15,
                "abstract": "High-performance ceramic separator membranes configured to eliminate dendritic sodium growth during fast charge cycles.",
                "tech_field": "Clean Energy"
            },
            {
                "patent_number": "US-12199876-B1",
                "title": "Autonomous Drone Swarm Collision Avoidance System",
                "assignee": "Stanford Robotics Lab",
                "filing_date": "2024-11-20",
                "grant_date": "2025-08-14",
                "status": "Active",
                "claims_count": 22,
                "abstract": "Decentralized mesh networks and spatial navigation protocols enabling collision-free flocking in high-density urban environments.",
                "tech_field": "Robotics & AI"
            },
            {
                "patent_number": "EP-4029110-A2",
                "title": "mRNA Delivery Nanoparticles with Lipid Shell Optimization",
                "assignee": "BioNTech Lab",
                "filing_date": "2025-03-01",
                "grant_date": None,
                "status": "Pending",
                "claims_count": 28,
                "abstract": "Formulations containing cationic ionizable lipids engineered for tissue-specific release of gene therapies.",
                "tech_field": "Biotechnology"
            },
            {
                "patent_number": "US-12245600-B2",
                "title": "Silicon Nitride Photonic Integrated Waveguide",
                "assignee": "Intel AI Research",
                "filing_date": "2024-07-12",
                "grant_date": "2025-12-10",
                "status": "Active",
                "claims_count": 19,
                "abstract": "Ultra-low-loss waveguides for optical computing and fiber-to-the-chip transceiver interconnects.",
                "tech_field": "Quantum Hardware"
            },
            {
                "patent_number": "US-12349001-B1",
                "title": "Self-Supervised Contrastive Learning Model for Medical Imagery",
                "assignee": "Harvard Health AI",
                "filing_date": "2025-01-20",
                "grant_date": "2025-10-02",
                "status": "Active",
                "claims_count": 14,
                "abstract": "Feature representation neural networks trained without manual annotation to classify MRI scans with high diagnostic accuracy.",
                "tech_field": "Robotics & AI"
            },
            {
                "patent_number": "EP-4112233-A1",
                "title": "High-Temperature Superconducting Tape for Fusion Reactors",
                "assignee": "Tokamak Energy",
                "filing_date": "2025-06-15",
                "grant_date": None,
                "status": "Pending",
                "claims_count": 26,
                "abstract": "Rare-earth barium copper oxide deposition techniques enhancing current densities in high magnetic field confinement magnets.",
                "tech_field": "Clean Energy"
            },
            {
                "patent_number": "US-12401823-B2",
                "title": "Graphene-Enhanced Anodes for Fast-Charging Batteries",
                "assignee": "Tesla Ventures",
                "filing_date": "2025-02-10",
                "grant_date": "2026-03-24",
                "status": "Active",
                "claims_count": 21,
                "abstract": "Silicon-graphene composite structures mitigating volumetric expansion and preserving capacity retention.",
                "tech_field": "Clean Energy"
            }
        ]

        for pt in patents_data:
            db.add(Patent(**pt))

        # 5. Tech Trends
        tech_trends_data = [
            {
                "technology_name": "Autonomous AI Agents for Scientific Discovery",
                "category": "Artificial Intelligence",
                "growth_rate": 48.5,
                "readiness_level": 7,
                "adoption_stage": "Emerging",
                "market_size_est": "$18.5 Billion",
                "description": "Closed-loop robotic laboratory automation guided by LLM-driven hypothesis generation and experimental validation."
            },
            {
                "technology_name": "Quantum Key Distribution (QKD) Satellite Networks",
                "category": "Quantum Technology",
                "growth_rate": 32.0,
                "readiness_level": 6,
                "adoption_stage": "Emerging",
                "market_size_est": "$6.2 Billion",
                "description": "Global space-based quantum encryption infrastructure protecting critical energy grid and financial data."
            },
            {
                "technology_name": "Solid-State Electrolyte Batteries for Aviation",
                "category": "Clean Energy",
                "growth_rate": 41.2,
                "readiness_level": 8,
                "adoption_stage": "Growth",
                "market_size_est": "$42.0 Billion",
                "description": "High energy density (500 Wh/kg) non-flammable battery cells engineered for regional zero-emission aircraft."
            },
            {
                "technology_name": "Neuromorphic Computing Chips for Edge AI",
                "category": "Artificial Intelligence",
                "growth_rate": 45.2,
                "readiness_level": 5,
                "adoption_stage": "Emerging",
                "market_size_est": "$12.4 Billion",
                "description": "Spike-timing-dependent plasticity silicon arrays enabling real-time on-chip training with sub-milliwatt power draw."
            },
            {
                "technology_name": "CRISPR-based Epigenetic Editing for Rare Diseases",
                "category": "Biotechnology",
                "growth_rate": 52.8,
                "readiness_level": 4,
                "adoption_stage": "Emerging",
                "market_size_est": "$8.9 Billion",
                "description": "Programmable dCas9-effector fusion systems silencing target disease genes without introducing permanent double-strand breaks."
            },
            {
                "technology_name": "Perovskite Tandem Solar Cell Commercialization",
                "category": "Clean Energy",
                "growth_rate": 36.5,
                "readiness_level": 8,
                "adoption_stage": "Mature",
                "market_size_est": "$54.2 Billion",
                "description": "Large-format crystalline perovskite-on-silicon panels achieving high power output in commercial solar projects."
            },
            {
                "technology_name": "Generative AI Code Synthesizers",
                "category": "Artificial Intelligence",
                "growth_rate": 64.0,
                "readiness_level": 9,
                "adoption_stage": "Mature",
                "market_size_est": "$38.5 Billion",
                "description": "Automated programming LLMs fine-tuned on secure enterprise code repositories to write high-fidelity backend handlers."
            },
            {
                "technology_name": "Magnetically Confined Aneutronic Fusion Power",
                "category": "Clean Energy",
                "growth_rate": 28.6,
                "readiness_level": 3,
                "adoption_stage": "Emerging",
                "market_size_est": "$150.0 Billion",
                "description": "Boron-11 proton plasma confinement reactors targeting direct electrical conversion without neutron radiation hazards."
            }
        ]

        for tt in tech_trends_data:
            db.add(TechTrend(**tt))

        # 6. Pre-computed Innovation Scores
        scores_data = [
            {
                "entity_type": "Research",
                "entity_name": "De Novo Molecular Design Pipeline",
                "novelty_score": 92.5,
                "patent_strength": 84.0,
                "tech_maturity": 75.0,
                "market_potential": 95.0,
                "funding_relevance": 90.0,
                "overall_score": 87.6,
                "recommendations": "High commercial potential! Recommended for fast-track spin-off or technology licensing."
            },
            {
                "entity_type": "Startup",
                "entity_name": "Quantum Dynamics Microprocessors",
                "novelty_score": 96.0,
                "patent_strength": 91.0,
                "tech_maturity": 68.0,
                "market_potential": 88.0,
                "funding_relevance": 94.0,
                "overall_score": 87.7,
                "recommendations": "Advance Technology Readiness Level (TRL) through bench scale prototyping and experimental validation."
            }
        ]

        for sc in scores_data:
            db.add(InnovationScore(**sc))

        # 7. Commercialization Opportunities
        comm_data = [
            {
                "title": "AI Drug Discovery Engine Licensing Opportunity",
                "insight_type": "Licensing",
                "description": "Exclusive pharmaceutical license available for AI protein-folding software suite proven against G-protein coupled receptors.",
                "target_industry": "Pharmaceuticals & Biotechnology",
                "estimated_value": "$12.5M Licensing Deal",
                "readiness": "High",
                "contact_email": "techtransfer@university.edu"
            },
            {
                "title": "Quantum Sensor Spin-off Seed Opportunity",
                "insight_type": "Startup Spin-off",
                "description": "Early-stage spin-off producing diamond nitrogen-vacancy magnetometers for biomedical imaging and defense navigation.",
                "target_industry": "Medical Imaging & Defense",
                "estimated_value": "$3.0M Seed Round",
                "readiness": "Medium",
                "contact_email": "invest@quantumventures.io"
            }
        ]

        for co in comm_data:
            db.add(CommercializationOpportunity(**co))

        # 8. Notifications
        notif_data = [
            {
                "user_id": db_users[0].id,
                "title": "New High-Match Funding Opportunity Available",
                "message": "ARPA-H Health AI Grant matches your profile keywords with a 94% eligibility confidence score.",
                "type": "funding"
            },
            {
                "user_id": db_users[0].id,
                "title": "Patent Citation Alert",
                "message": "Your patent US-11984201-B2 was cited by Google DeepMind in a recent international filing.",
                "type": "patent"
            }
        ]

        for n in notif_data:
            db.add(Notification(**n))

        db.commit()
        logger.info("Successfully seeded 10 Users, 5 Grants, 3 Publications, 3 Patents, 3 Tech Trends, Scores, Commercialization, & Notifications.")
        return {"message": "Database seeded successfully with sample platform data."}

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        return {"error": str(e)}

def migrate_old_urls(db: Session):
    try:
        mapping = {
            "https://arpa-h.gov/grants/2026-ai-health": "https://arpa-h.gov/engage-and-connect/opportunities",
            "https://seedfund.nsf.gov/portfolio/quantum": "https://seedfund.nsf.gov/",
            "https://eic.ec.europa.eu/horizon-2026-energy": "https://eic.ec.europa.eu/",
            "https://commonfund.nih.gov/tra": "https://commonfund.nih.gov/",
            "https://energy.gov/eere/grid-2026": "https://www.energy.gov/"
        }
        for old_url, new_url in mapping.items():
            db.query(FundingOpportunity).filter(FundingOpportunity.url == old_url).update({FundingOpportunity.url: new_url})
        db.commit()
    except Exception as e:
        logger.error(f"Error migrating old URLs: {e}")
