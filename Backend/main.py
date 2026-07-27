from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Base,User,Profile,Grant,Research
from models import Patent
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
@app.post("/patent")
def add_patent(data: PatentData):
    db = SessionLocal()

    patent = Patent(
        title=data.title,
        inventor=data.inventor,
        status=data.status
    )

    db.add(patent)
    db.commit()
    db.close()

    return {"message": "Patent Added Successfully"}
@app.get("/patent")
def get_patents():
    db = SessionLocal()
    patents = db.query(Patent).all()
    db.close()
    return patents
@app.delete("/patent/{patent_id}")
def delete_patent(patent_id: int):
    db = SessionLocal()

    patent = db.query(Patent).filter(Patent.id == patent_id).first()

    if patent:
        db.delete(patent)
        db.commit()

    db.close()

    return {"message": "Patent Deleted Successfully"}
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