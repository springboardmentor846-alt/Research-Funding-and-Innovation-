from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Base,User,Profile,Grant,Research
from models import Patent,Technology,Innovation,Commercialization
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SessionLocal = sessionmaker(bind=engine)

class ProfileData(BaseModel):
    name: str
    department: str
    research_area: str
    email: str


class LoginData(BaseModel):
    email: str
    password: str
class GrantData(BaseModel):
    title: str
    research_field: str
    funding_amount: float
    eligibility: str
    description: str
class ResearchData(BaseModel):
    title: str
    researcher: str
    department: str
    research_area: str
    status: str
class PatentData(BaseModel):
    title: str
    inventor: str
    patent_id: str
    status: str
class TechnologyData(BaseModel):
    name: str
    patents: int
class InnovationData(BaseModel):
    title: str
    patents:int
    trend: str
    market_potential: str
class CommercializationData(BaseModel):
    title: str
    industry: str
    market_potential: str

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/funding")
def funding():
    return [
        {
            "agency": "DST",
            "grant": "AI Research",
            "amount": "₹50 Lakhs"
        },
        {
            "agency": "DRDO",
            "grant": "Defence Innovation",
            "amount": "₹1 Cr"
        }
    ]
@app.post("/login")
def login(data: LoginData):
    if data.email == "debastutisahoo@gmail.com" and data.password == "1234":
        return {
            "message": "Login Successful",
            "role": "Admin"
        }

    return {
        "message": "Invalid Email or Password"
    }
@app.post("/profile")
def save_profile(data: ProfileData):
    db = SessionLocal()

    profile = Profile(
        name=data.name,
        department=data.department,
        research_area=data.research_area,
        email=data.email
    )

    db.add(profile)
    db.commit()
    db.close()

    return {
        "message": "Profile Saved Successfully"
    }
@app.get("/publications")
def get_publications():
    return [
        {
            "title": "AI in Healthcare",
            "author": "John",
            "year": 2024
        },
        {
            "title": "Machine Learning",
            "author": "Alice",
            "year": 2023
        }
    ]
@app.get("/patent")
def get_patents():
    db = SessionLocal()
    patents = db.query(Patent).all()
    db.close()
    return patents
@app.post("/grant")
def add_grant(data: GrantData):
    db = SessionLocal()

    grant = Grant(
        title=data.title,
        research_field=data.research_field,
        funding_amount=data.funding_amount,
        eligibility=data.eligibility,
        description=data.description
    )

    db.add(grant)
    db.commit()
    db.close()

    return {"message": "Grant Saved Successfully"}
@app.get("/grants")
def get_grants():
    db = SessionLocal()

    grants = db.query(Grant).all()

    db.close()

    return grants
@app.get("/profiles")
def get_profiles():
    db = SessionLocal()

    profiles = db.query(Profile).all()

    db.close()

    return profiles
@app.get("/recommend/{research_area}")
def recommend_grants(research_area: str):

    if research_area.lower() == "ai":
        return [
            {
                "grant": "AI Research Grant",
                "agency": "DST",
                "amount": "₹50 Lakhs"
            }
        ]

    elif research_area.lower() == "cyber security":
        return [
            {
                "grant": "Cyber Security Grant",
                "agency": "DRDO",
                "amount": "₹1 Crore"
            }
        ]

    elif research_area.lower() == "machine learning":
        return [
            {
                "grant": "ML Innovation Grant",
                "agency": "AICTE",
                "amount": "₹30 Lakhs"
            }
        ]

    else:
        return [
            {
                "grant": "General Research Grant",
                "agency": "UGC",
                "amount": "₹10 Lakhs"
            }
        ]
@app.get("/match/{research_area}")
def match_grants(research_area: str):
    db = SessionLocal()

    grants = db.query(Grant).filter(
        Grant.research_field.ilike(f"%{research_area}%")
    ).all()

    db.close()

    return grants
@app.get("/publication-trends")
def publication_trends():
    return [
        {"year": 2020, "publications": 12},
        {"year": 2021, "publications": 18},
        {"year": 2022, "publications": 26},
        {"year": 2023, "publications": 35},
        {"year": 2024, "publications": 42}
    ]
@app.get("/dashboard")
def dashboard():
    db = SessionLocal()

    try:
        return {
            "researchers": db.query(Profile).count(),
            "grants": db.query(Grant).count(),
            "publications": 2,
            "patents": 2
        }
    finally:
        db.close()
@app.post("/research")
def add_research(data: ResearchData):
    db = SessionLocal()

    research = Research(
        title=data.title,
        researcher=data.researcher,
        department=data.department,
        research_area=data.research_area,
        status=data.status
    )

    db.add(research)
    db.commit()
    db.close()

    return {"message": "Research Added Successfully"}
@app.get("/research")
def get_research():
    db = SessionLocal()

    research = db.query(Research).all()

    db.close()

    return research
@app.delete("/research/{research_id}")
def delete_research(research_id: int):
    db = SessionLocal()

    research = db.query(Research).filter(
        Research.id == research_id
    ).first()

    if not research:
        db.close()
        return {"message": "Research not found"}

    db.delete(research)
    db.commit()
    db.close()

    return {"message": "Research Deleted Successfully"}
@app.post("/patent")
def add_patent(data: PatentData):
    db = SessionLocal()

    patent = Patent(
        title=data.title,
        inventor=data.inventor,
        patent_id=data.patent_id,
        status=data.status
    )

    db.add(patent)
    db.commit()
    db.close()

    return {"message": "Patent Added Successfully"}
@app.delete("/patent/{id}")
def delete_patent(id: int):
    db = SessionLocal()

    patent = db.query(Patent).filter(Patent.id == id).first()

    if patent:
        db.delete(patent)
        db.commit()

    db.close()

    return {"message": "Patent Deleted Successfully"}
@app.delete("/profile/{profile_id}")
def delete_profile(profile_id: int):
    db = SessionLocal()

    profile = db.query(Profile).filter(Profile.id == profile_id).first()

    if profile:
        db.delete(profile)
        db.commit()

    db.close()

    return {"message": "Profile Deleted Successfully"}
@app.post("/technology")
def add_technology(data: TechnologyData):
    db = SessionLocal()

    # Dynamic trend calculation
    if data.patents >= 10:
        trend = "Growing"
    elif data.patents >= 5:
        trend = "Stable"
    else:
        trend = "Declining"

    technology = Technology(
        name=data.name,
        patents=data.patents,
        trend=trend
    )

    db.add(technology)
    db.commit()
    db.refresh(technology)
    db.close()

    return {
        "message": "Technology Added Successfully",
        "trend": trend
    }
@app.get("/technology")
def get_technology():
    db = SessionLocal()

    technologies = db.query(Technology).all()

    db.close()

    return technologies
@app.delete("/technology/{id}")
def delete_technology(id: int):
    db = SessionLocal()

    technology = db.query(Technology).filter(Technology.id == id).first()

    if technology:
        db.delete(technology)
        db.commit()

    db.close()

    return {"message": "Technology Deleted Successfully"}
@app.post("/innovation")
def add_innovation(data: InnovationData):
    db = SessionLocal()

    score = 0

    # Patent score
    if data.patents >= 10:
        score += 40
    elif data.patents >= 5:
        score += 30
    else:
        score += 20

    # Technology trend score
    if data.trend.lower() == "growing":
        score += 30
    elif data.trend.lower() == "stable":
        score += 20
    else:
        score += 10

    # Market potential score
    if data.market_potential.lower() == "high":
        score += 30
    elif data.market_potential.lower() == "medium":
        score += 20
    else:
        score += 10

    # Automatic level
    if score >= 80:
        level = "High"
    elif score >= 60:
        level = "Medium"
    else:
        level = "Low"

    innovation = Innovation(
        title=data.title,
        score=score,
        level=level
    )

    db.add(innovation)
    db.commit()
    db.refresh(innovation)
    db.close()

    return {
        "message": "Innovation Added Successfully",
        "score": score,
        "level": level
    }
@app.get("/innovation")
def get_innovation():
    db = SessionLocal()

    innovations = db.query(Innovation).all()

    db.close()

    return innovations
@app.delete("/innovation/{id}")
def delete_innovation(id: int):
    db = SessionLocal()

    innovation = db.query(Innovation).filter(
        Innovation.id == id
    ).first()

    if innovation:
        db.delete(innovation)
        db.commit()

    db.close()

    return {"message": "Innovation Deleted Successfully"}
@app.post("/commercialization")
def add_commercialization(data: CommercializationData):
    db = SessionLocal()

    # Dynamic recommendation
    if data.market_potential.lower() == "high":
        recommendation = "Launch / Commercialize"
    elif data.market_potential.lower() == "medium":
        recommendation = "Pilot Testing"
    else:
        recommendation = "Further Research"

    commercialization = Commercialization(
        title=data.title,
        industry=data.industry,
        market_potential=data.market_potential,
        recommendation=recommendation
    )

    db.add(commercialization)
    db.commit()
    db.refresh(commercialization)
    db.close()

    return {
        "message": "Commercialization Added Successfully",
        "recommendation": recommendation
    }
@app.get("/commercialization")
def get_commercialization():
    db = SessionLocal()

    commercialization = db.query(Commercialization).all()

    db.close()

    return commercialization
@app.delete("/commercialization/{id}")
def delete_commercialization(id: int):
    db = SessionLocal()

    commercialization = db.query(Commercialization).filter(
        Commercialization.id == id
    ).first()

    if commercialization:
        db.delete(commercialization)
        db.commit()

    db.close()

    return {"message": "Commercialization Deleted Successfully"}
@app.get("/innovation-dashboard")
def innovation_dashboard():
    db = SessionLocal()

    data = {
        "patents": db.query(Patent).count(),
        "technologies": db.query(Technology).count(),
        "innovations": db.query(Innovation).count(),
        "commercialization": db.query(Commercialization).count()
    }

    db.close()

    return data