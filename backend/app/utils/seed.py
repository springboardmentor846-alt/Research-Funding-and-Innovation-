from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.core.security import hash_password
from app.db import SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.publication import Publication
from app.models.collaboration import Collaboration
from app.models.funding_history import FundingHistory


DEMO_USERS = [
    {
        "email": "researcher@demo.com",
        "username": "researcher",
        "full_name": "Dr. Alice Researcher",
        "password": "Research@2026",
        "role": UserRole.RESEARCHER,
        "affiliation": "MIT",
        "research_interests": "machine learning, deep learning, medical imaging, computer vision",
        "skills": "Python, TensorFlow, PyTorch, Data Analysis",
        "bio": "AI researcher focusing on healthcare applications.",
        "h_index": 12,
        "i10_index": 8,
        "citation_count": 540,
    },
    {
        "email": "founder@demo.com",
        "username": "founder",
        "full_name": "Bob Startup",
        "password": "Startup@2026",
        "role": UserRole.STARTUP_FOUNDER,
        "affiliation": "InnovateTech Inc.",
        "bio": "Building next-generation medical AI tools.",
    },
    {
        "email": "innovation@demo.com",
        "username": "innovation",
        "full_name": "Carol Innovation",
        "password": "Innovate@2026",
        "role": UserRole.INNOVATION_MANAGER,
        "affiliation": "Stanford University",
        "bio": "Managing innovation portfolio.",
    },
    {
        "email": "admin@demo.com",
        "username": "admin",
        "full_name": "Platform Admin",
        "password": "Admin@2026",
        "role": UserRole.ADMIN,
    },
]


DEMO_FUNDING = [
    {
        "title": "NIH R01 - Artificial Intelligence in Healthcare",
        "description": "Supports research projects that develop and apply artificial intelligence and machine learning methods to address biomedical and health-related challenges.",
        "keywords": "machine learning, deep learning, medical imaging, healthcare, biomedical, AI",
        "research_domain": "Medical AI",
        "organization": "National Institutes of Health (NIH)",
        "country": "USA",
        "funding_type": "grant",
        "amount_min": 250000,
        "amount_max": 500000,
        "currency": "USD",
        "eligibility": "Principal Investigators at accredited institutions in the United States.",
        "url": "https://grants.nih.gov",
    },
    {
        "title": "NSF Computer and Information Science Research",
        "description": "Supports research that advances the theoretical understanding of computing and information processing.",
        "keywords": "computer science, algorithms, machine learning, NLP, data science",
        "research_domain": "Computer Science",
        "organization": "National Science Foundation (NSF)",
        "country": "USA",
        "funding_type": "grant",
        "amount_min": 100000,
        "amount_max": 1200000,
        "currency": "USD",
        "eligibility": "Faculty members at US universities.",
        "url": "https://www.nsf.gov",
    },
    {
        "title": "EU Horizon Europe - AI Excellence",
        "description": "Funding for cutting-edge AI research and innovation across Europe, including trustworthy AI and AI for health.",
        "keywords": "artificial intelligence, deep learning, trustworthy AI, health, machine learning",
        "research_domain": "Artificial Intelligence",
        "organization": "European Commission",
        "country": "International",
        "funding_type": "grant",
        "amount_min": 500000,
        "amount_max": 5000000,
        "currency": "EUR",
        "eligibility": "Consortia of European institutions.",
        "url": "https://ec.europa.eu/info/funding-tenders",
    },
    {
        "title": "Bill & Melinda Gates Foundation - Global Health AI",
        "description": "Grand Challenges grants for AI solutions to global health problems in low- and middle-income countries.",
        "keywords": "global health, machine learning, diagnostics, public health, AI",
        "research_domain": "Public Health",
        "organization": "Gates Foundation",
        "country": "International",
        "funding_type": "grant",
        "amount_min": 100000,
        "amount_max": 1000000,
        "currency": "USD",
        "eligibility": "Researchers worldwide.",
        "url": "https://www.gatesfoundation.org",
    },
    {
        "title": "Wellcome Trust - Mental Health Research",
        "description": "Funding for innovative research in mental health, including digital phenotyping and AI-driven biomarkers.",
        "keywords": "mental health, digital health, AI, biomarkers, neuroimaging",
        "research_domain": "Mental Health",
        "organization": "Wellcome Trust",
        "country": "UK",
        "funding_type": "grant",
        "amount_min": 50000,
        "amount_max": 1500000,
        "currency": "GBP",
        "eligibility": "Researchers globally; UK institutions receive preference.",
        "url": "https://wellcome.org",
    },
    {
        "title": "DARPA Artificial Intelligence Exploration",
        "description": "High-risk, high-reward AI research for defense applications including autonomous systems and trustworthy AI.",
        "keywords": "autonomous systems, AI, robotics, deep learning, reinforcement learning",
        "research_domain": "Defense AI",
        "organization": "DARPA",
        "country": "USA",
        "funding_type": "grant",
        "amount_min": 250000,
        "amount_max": 1000000,
        "currency": "USD",
        "eligibility": "US-based organizations.",
        "url": "https://www.darpa.mil",
    },
    {
        "title": "Y Combinator Research Fellowship",
        "description": "Seed funding for founders turning research into startups. Non-dilutive grants plus mentorship.",
        "keywords": "startup, commercialization, entrepreneurship, deep tech, AI",
        "research_domain": "Entrepreneurship",
        "organization": "Y Combinator",
        "country": "International",
        "funding_type": "fellowship",
        "amount_min": 500000,
        "amount_max": 1000000,
        "currency": "USD",
        "eligibility": "Founders with research-backed technology.",
        "url": "https://www.ycombinator.com",
    },
    {
        "title": "Google AI for Social Good",
        "description": "Grants for researchers using AI to address humanitarian and environmental challenges.",
        "keywords": "AI for good, social impact, environment, sustainability, machine learning",
        "research_domain": "Social Impact",
        "organization": "Google.org",
        "country": "International",
        "funding_type": "grant",
        "amount_min": 100000,
        "amount_max": 500000,
        "currency": "USD",
        "eligibility": "Nonprofits and academic institutions.",
        "url": "https://www.google.org",
    },
    {
        "title": "Cancer Research UK - AI in Oncology",
        "description": "Funding for AI-driven approaches to cancer detection, diagnosis, and treatment planning.",
        "keywords": "oncology, cancer, medical imaging, AI, deep learning, diagnostics",
        "research_domain": "Oncology",
        "organization": "Cancer Research UK",
        "country": "UK",
        "funding_type": "grant",
        "amount_min": 200000,
        "amount_max": 2000000,
        "currency": "GBP",
        "eligibility": "UK-based research institutions.",
        "url": "https://www.cancerresearchuk.org",
    },
    {
        "title": "NASA - AI for Earth Science",
        "description": "Funding for AI/ML approaches to climate, weather, and earth system modeling.",
        "keywords": "climate, earth science, machine learning, remote sensing, AI",
        "research_domain": "Climate",
        "organization": "NASA",
        "country": "USA",
        "funding_type": "grant",
        "amount_min": 100000,
        "amount_max": 1500000,
        "currency": "USD",
        "eligibility": "US institutions and collaborators.",
        "url": "https://www.nasa.gov",
    },
]


DEMO_PUBLICATIONS = [
    {
        "title": "Deep Learning for Early Detection of Lung Cancer in CT Scans",
        "abstract": "We propose a transformer-based architecture for the early detection of lung nodules in low-dose CT scans. Our model achieves state-of-the-art performance on the LIDC-IDRI dataset with 96% sensitivity.",
        "authors": "Alice Researcher, John Smith, Maria Garcia",
        "keywords": "deep learning, medical imaging, lung cancer, CT, transformer",
        "doi": "10.1234/lung-cancer-2024.001",
        "publisher": "Nature Medicine",
        "research_domain": "Medical AI",
        "venue": "Nature Medicine",
        "citation_count": 87,
    },
    {
        "title": "Federated Learning for Multi-Hospital Patient Data Analysis",
        "abstract": "We present a privacy-preserving federated learning framework that allows hospitals to collaboratively train AI models without sharing raw patient data.",
        "authors": "Alice Researcher, Sarah Lee",
        "keywords": "federated learning, privacy, healthcare, machine learning",
        "doi": "10.1234/federated-health-2024.002",
        "publisher": "JAMA",
        "research_domain": "Medical AI",
        "venue": "JAMA",
        "citation_count": 54,
    },
    {
        "title": "Attention Mechanisms for Medical Image Segmentation: A Survey",
        "abstract": "A comprehensive survey of attention mechanisms applied to medical image segmentation tasks across CT, MRI, and ultrasound modalities.",
        "authors": "Alice Researcher, Wei Chen",
        "keywords": "attention, segmentation, medical imaging, deep learning",
        "doi": "10.1234/attention-survey-2023.003",
        "publisher": "IEEE TMI",
        "research_domain": "Medical AI",
        "venue": "IEEE Transactions on Medical Imaging",
        "citation_count": 123,
    },
]


def seed_users(db: Session) -> None:
    if db.query(User).count() > 0:
        logger.info("Users already seeded, skipping")
        return
    for u in DEMO_USERS:
        user = User(
            email=u["email"],
            username=u["username"],
            full_name=u.get("full_name"),
            hashed_password=hash_password(u["password"]),
            role=u["role"],
            affiliation=u.get("affiliation"),
            research_interests=u.get("research_interests"),
            skills=u.get("skills"),
            bio=u.get("bio"),
            h_index=u.get("h_index", 0),
            i10_index=u.get("i10_index", 0),
            citation_count=u.get("citation_count", 0),
            is_verified=True,
        )
        db.add(user)
    db.commit()
    logger.info(f"Seeded {len(DEMO_USERS)} users")


def seed_funding(db: Session) -> None:
    """No-op: funding is sourced from external providers via the Funding
    Intelligence Service. Trigger an initial sync from the admin Funding
    page after seeding the rest of the platform.
    """
    logger.info("Funding seeding skipped — populated by the Funding Intelligence Service.")


def seed_publications(db: Session) -> None:
    if db.query(Publication).count() > 0:
        logger.info("Publications already seeded, skipping")
        return
    researcher = db.query(User).filter(User.username == "researcher").first()
    if not researcher:
        return
    for p in DEMO_PUBLICATIONS:
        pub = Publication(
            owner_id=researcher.id,
            publication_date=datetime.utcnow() - timedelta(days=180),
            **p,
        )
        db.add(pub)
    db.commit()
    logger.info(f"Seeded {len(DEMO_PUBLICATIONS)} publications for researcher")


def seed_collaborations(db: Session) -> None:
    if db.query(Collaboration).count() > 0:
        logger.info("Collaborations already seeded, skipping")
        return
    researcher = db.query(User).filter(User.username == "researcher").first()
    if not researcher:
        return
    samples = [
        {
            "collaborator_name": "Dr. John Smith",
            "collaborator_email": "jsmith@stanford.edu",
            "collaborator_affiliation": "Stanford University",
            "project_title": "AI for Cancer Imaging",
            "description": "Joint research on transformer architectures for tumor detection.",
            "status": "active",
            "start_date": datetime.utcnow() - timedelta(days=120),
        },
        {
            "collaborator_name": "Dr. Maria Garcia",
            "collaborator_email": "mgarcia@mit.edu",
            "collaborator_affiliation": "MIT CSAIL",
            "project_title": "Privacy-Preserving Federated Learning",
            "description": "Multi-hospital federated learning framework.",
            "status": "completed",
            "start_date": datetime.utcnow() - timedelta(days=400),
            "end_date": datetime.utcnow() - timedelta(days=60),
        },
    ]
    for c in samples:
        db.add(Collaboration(owner_id=researcher.id, **c))
    db.commit()
    logger.info(f"Seeded {len(samples)} collaborations for researcher")


def seed_funding_history(db: Session) -> None:
    if db.query(FundingHistory).count() > 0:
        logger.info("Funding history already seeded, skipping")
        return
    researcher = db.query(User).filter(User.username == "researcher").first()
    if not researcher:
        return
    samples = [
        {
            "title": "NSF CAREER Award (2024)",
            "organization": "National Science Foundation",
            "amount": 500000.0,
            "currency": "USD",
            "status": "awarded",
            "awarded_date": datetime.utcnow() - timedelta(days=300),
            "end_date": datetime.utcnow() + timedelta(days=430),
            "description": "Five-year faculty early career development grant.",
        },
        {
            "title": "Google AI Faculty Research Award",
            "organization": "Google Research",
            "amount": 75000.0,
            "currency": "USD",
            "status": "completed",
            "awarded_date": datetime.utcnow() - timedelta(days=600),
            "end_date": datetime.utcnow() - timedelta(days=200),
            "description": "One-year unrestricted research gift.",
        },
    ]
    for h in samples:
        db.add(FundingHistory(owner_id=researcher.id, **h))
    db.commit()
    logger.info(f"Seeded {len(samples)} funding history records for researcher")


def run() -> None:
    """Run the full seed pipeline."""
    init_db()
    db = SessionLocal()
    try:
        seed_users(db)
        seed_funding(db)
        seed_publications(db)
        seed_collaborations(db)
        seed_funding_history(db)
    finally:
        db.close()
    logger.info("Seed complete")


if __name__ == "__main__":
    run()
