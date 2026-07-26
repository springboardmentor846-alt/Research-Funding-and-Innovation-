import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.funding import FundingOpportunity
from app.models.publication import Publication
from app.models.profile import ResearcherProfile
from app.auth.security import hash_password
from datetime import date

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Test User ──────────────────────────────────────────────
if not db.query(User).filter(User.email == "test@test.com").first():
    db.add(User(
        name="Test Researcher",
        email="test@test.com",
        password=hash_password("test1234"),
        role="researcher"
    ))
    db.commit()
    print("[OK] Test user created  ->  test@test.com / test1234")
else:
    print("[OK] Test user already exists")

user = db.query(User).filter(User.email == "test@test.com").first()

# ── Test Profile ───────────────────────────────────────────
if not db.query(ResearcherProfile).filter(ResearcherProfile.user_id == user.id).first():
    db.add(ResearcherProfile(
        user_id=user.id,
        organization="MIT",
        designation="Senior Researcher",
        research_domain="Artificial Intelligence",
        keywords="deep learning, machine learning, NLP, computer vision",
        biography="Experienced researcher in AI and machine learning."
    ))
    db.commit()
    print("[OK] Test profile created")

# ── Funding Opportunities ──────────────────────────────────
funding_data = [
    ("AI Research Innovation Grant", "National Science Foundation", 500000, date(2025, 9, 30), "USA", "Artificial Intelligence", "Open to universities and research institutions with active AI programs", "Funding for cutting-edge AI research including machine learning, NLP, and computer vision projects.", "https://nsf.gov/apply"),
    ("Climate Change & Sustainability Fund", "European Research Council", 750000, date(2025, 8, 15), "EU", "Environmental Science", "Open to EU-based research institutions and universities", "Supporting research on climate change mitigation, renewable energy, and sustainable development.", "https://erc.europa.eu/apply"),
    ("Biomedical Research Excellence Award", "NIH", 1200000, date(2025, 10, 1), "USA", "Biomedical", "Open to accredited medical schools and biomedical research centers", "Advancing biomedical research in genomics, drug discovery, and personalized medicine.", "https://nih.gov/grants"),
    ("Quantum Computing Research Initiative", "DARPA", 2000000, date(2025, 7, 31), "USA", "Quantum Computing", "Open to universities and national laboratories with quantum research facilities", "Accelerating quantum computing hardware and algorithm development.", "https://darpa.mil/apply"),
    ("Global Health Innovation Fund", "WHO", 300000, date(2025, 11, 30), "Global", "Public Health", "Open to NGOs, universities, and health research institutions worldwide", "Supporting innovative solutions to global health challenges.", "https://who.int/grants"),
    ("Cybersecurity Research Program", "DHS", 450000, date(2025, 8, 31), "USA", "Cybersecurity", "Open to US-based universities and research labs", "Research on advanced cybersecurity threats and critical infrastructure protection.", "https://dhs.gov/research"),
    ("Renewable Energy Technology Grant", "Department of Energy", 900000, date(2025, 12, 15), "USA", "Energy", "Open to universities, national labs, and private research institutions", "Developing next-generation solar, wind, and energy storage technologies.", "https://energy.gov/grants"),
    ("Data Science & Analytics Fellowship", "Gates Foundation", 250000, date(2025, 9, 15), "Global", "Data Science", "Open to researchers from developing countries and global institutions", "Applying data science to solve humanitarian challenges.", "https://gatesfoundation.org/apply"),
    ("Robotics & Automation Research Fund", "IEEE Foundation", 350000, date(2025, 10, 31), "Global", "Robotics", "Open to universities and research institutions with robotics programs", "Advancing robotics research in autonomous systems and human-robot interaction.", "https://ieee.org/grants"),
    ("Neuroscience Discovery Grant", "Brain Research Foundation", 600000, date(2025, 11, 15), "USA", "Neuroscience", "Open to accredited neuroscience research centers and universities", "Exploring brain function, neurological disorders, and cognitive science.", "https://brainresearch.org/grants"),
    ("Space Technology Research Award", "NASA", 1500000, date(2025, 7, 15), "USA", "Aerospace", "Open to universities and aerospace research institutions", "Research on space exploration technologies and satellite systems.", "https://nasa.gov/grants"),
    ("Agricultural Innovation Fund", "USDA", 400000, date(2025, 10, 15), "USA", "Agriculture", "Open to agricultural universities and research stations", "Developing sustainable farming technologies and food security solutions.", "https://usda.gov/grants"),
]

existing = db.query(FundingOpportunity).count()
if existing == 0:
    for f in funding_data:
        db.add(FundingOpportunity(
            title=f[0], agency=f[1], funding_amount=f[2], deadline=f[3],
            country=f[4], research_domain=f[5], eligibility=f[6],
            description=f[7], application_link=f[8], status="Open"
        ))
    db.commit()
    print(f"[OK] {len(funding_data)} funding opportunities created")
else:
    print(f"[OK] Funding opportunities already exist ({existing})")

# ── Publications ───────────────────────────────────────────
pub_data = [
    ("Deep Learning for Medical Image Analysis", 2023, "Ahmed K., Smith J., Lee M.", 145, "Artificial Intelligence", "deep learning, medical imaging, CNN, diagnosis", "MIT"),
    ("Climate Modeling with Neural Networks", 2022, "Johnson R., Patel S.", 89, "Environmental Science", "climate change, neural networks, prediction, modeling", "Stanford University"),
    ("CRISPR Gene Editing Advances", 2023, "Williams T., Brown A., Davis C.", 210, "Biomedical", "CRISPR, gene editing, genomics, therapy", "Harvard Medical School"),
    ("Quantum Entanglement in Computing", 2021, "Chen X., Kumar V.", 178, "Quantum Computing", "quantum computing, entanglement, qubits, algorithms", "Caltech"),
    ("COVID-19 Vaccine Efficacy Study", 2022, "Martinez L., Thompson K.", 320, "Public Health", "vaccine, COVID-19, efficacy, immunology", "Johns Hopkins"),
    ("Zero-Trust Security Architecture", 2023, "Anderson P., White S.", 67, "Cybersecurity", "cybersecurity, zero-trust, network security, authentication", "Carnegie Mellon"),
    ("Perovskite Solar Cell Efficiency", 2022, "Taylor R., Jackson M.", 134, "Energy", "solar energy, perovskite, efficiency, renewable", "NREL"),
    ("Predictive Analytics in Healthcare", 2023, "Harris N., Clark B.", 98, "Data Science", "data science, healthcare, predictive analytics, machine learning", "University of Michigan"),
    ("Autonomous Robot Navigation", 2021, "Lewis D., Robinson E.", 156, "Robotics", "robotics, autonomous navigation, SLAM, sensors", "Georgia Tech"),
    ("Alzheimer Early Detection via MRI", 2022, "Walker F., Hall G.", 201, "Neuroscience", "neuroscience, Alzheimer, MRI, early detection", "Mayo Clinic"),
    ("Mars Terrain Analysis Using AI", 2023, "Young H., King I.", 88, "Aerospace", "space, Mars, AI, terrain analysis, NASA", "JPL"),
    ("Drought-Resistant Crop Engineering", 2021, "Scott J., Green K.", 112, "Agriculture", "agriculture, drought resistance, crop engineering, GMO", "Iowa State University"),
    ("Transformer Models for NLP", 2022, "Adams L., Baker M.", 445, "Artificial Intelligence", "NLP, transformers, BERT, language models", "Google Research"),
    ("Ocean Acidification Impact Study", 2021, "Carter N., Mitchell O.", 76, "Environmental Science", "ocean, acidification, climate, marine biology", "Woods Hole"),
    ("mRNA Therapeutics Development", 2023, "Perez P., Roberts Q.", 189, "Biomedical", "mRNA, therapeutics, drug delivery, vaccines", "Moderna Research"),
    ("Quantum Error Correction Methods", 2022, "Turner R., Phillips S.", 143, "Quantum Computing", "quantum, error correction, fault tolerance, qubits", "IBM Research"),
    ("Malaria Prevention in Sub-Saharan Africa", 2021, "Campbell T., Parker U.", 95, "Public Health", "malaria, prevention, Africa, public health", "WHO Research"),
    ("AI-Powered Intrusion Detection", 2023, "Evans V., Edwards W.", 72, "Cybersecurity", "AI, intrusion detection, cybersecurity, anomaly detection", "MIT Lincoln Lab"),
    ("Wind Turbine Optimization", 2022, "Collins X., Stewart Y.", 108, "Energy", "wind energy, turbine, optimization, renewable", "NREL"),
    ("Big Data in Financial Markets", 2021, "Morris Z., Rogers A.", 167, "Data Science", "big data, finance, analytics, machine learning", "Wharton School"),
]

existing_pubs = db.query(Publication).count()
if existing_pubs == 0:
    for p in pub_data:
        db.add(Publication(
            title=p[0], year=p[1], authors=p[2], citation_count=p[3],
            research_domain=p[4], keywords=p[5], organization=p[6]
        ))
    db.commit()
    print(f"[OK] {len(pub_data)} publications created")
else:
    print(f"[OK] Publications already exist ({existing_pubs})")

db.close()
print("\nSeeding complete! Login with  test@test.com / test1234")
