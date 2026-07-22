from unittest import result
from urllib import response
from fastapi import APIRouter
from models import user
from models.user import UserSignup
from app.database import engine
from sqlalchemy import text
from models.login import UserLogin
from app.security import hash_password, verify_password
from app.jwt_handler import create_access_token
from fastapi import Header
from app.jwt_handler import verify_token
from models.research_profile import ResearchProfile
from models.funding import FundingOpportunity
from models.publication import Publication
from models.patent import Patent


router = APIRouter()

@router.post("/signup")
def signup(user: UserSignup):

    print("Password received:", user.password)
    print("Password length:", len(user.password))

    query = text("""
        INSERT INTO users (name, email, password, role)
        VALUES (:name, :email, :password, :role)
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "name": user.name,
                "email": user.email,
                "password": hash_password(user.password),
                "role": user.role
            }
        )
        connection.commit()

    return {
        "message": "User registered and saved to database successfully"
    }
@router.post("/login")
def login(user: UserLogin):
    query = text("""
        SELECT password, role FROM users
        WHERE email = :email
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "email": user.email
            }
        ).fetchone()
    if result and verify_password(user.password, result[0]):
        token = create_access_token({"email": user.email, "role": result[1]})

        return {
        "message": "Login successful",
        "access_token": token
        }
    else:
        return {"message": "Invalid email or password"}   
from fastapi import Header

@router.get("/profile")
def profile(token: str = None):
    print("TOKEN =", token)

    if not token:
        return {"message": "Access denied"}

    payload = verify_token(token)

    if payload:
        return {
            "message": "Protected route accessed",
            "user": payload
        }
    else:
        return {"message": "Invalid token"}
@router.get("/research-dashboard")
def research_dashboard(token: str = None):
    if not token:
        return {"message": "Access denied"}

    payload = verify_token(token)

    if not payload:
        return {"message": "Invalid token"}

    if payload["role"] != "Researcher":
        return {"message": "Only Researcher can access this"}

    return {"message": "Welcome to Research Dashboard"}

@router.post("/create-research-profile")
def create_research_profile(profile: ResearchProfile):
    query = text("""
        INSERT INTO research_profiles
        (email, research_domain, keywords, publications, patents, technology_area, organization)
        VALUES
        (:email, :research_domain, :keywords, :publications, :patents, :technology_area, :organization)
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "email": profile.email,
                "research_domain": profile.research_domain,
                "keywords": profile.keywords,
                "publications": profile.publications,
                "patents": profile.patents,
                "technology_area": profile.technology_area,
                "organization": profile.organization
            }
        )
        connection.commit()

    return {"message": "Research profile created successfully"}

@router.post("/create-funding")
def create_funding(funding: FundingOpportunity):
    query = text("""
        INSERT INTO funding_opportunities
        (funding_name, domain, amount, eligibility, deadline)
        VALUES
        (:funding_name, :domain, :amount, :eligibility, :deadline)
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "funding_name": funding.funding_name,
                "domain": funding.domain,
                "amount": funding.amount,
                "eligibility": funding.eligibility,
                "deadline": funding.deadline
            }
        )
        connection.commit()

    return {"message": "Funding opportunity created successfully"}

@router.post("/create-publication")
def create_publication(publication: Publication):

    query = text("""
        INSERT INTO publications
        (email, title, authors, journal, publication_year)
        VALUES
        (:email, :title, :authors, :journal, :publication_year)
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "email": publication.email,
                "title": publication.title,
                "authors": publication.authors,
                "journal": publication.journal,
                "publication_year": publication.publication_year
            }
        )
        connection.commit()

    return {
        "message": "Publication added successfully"
    }


@router.post("/create-patent")
def create_patent(patent: Patent):

    query = text("""
        INSERT INTO patents
        (email, patent_title, patent_number, technology_domain, filing_date)
        VALUES
        (:email, :patent_title, :patent_number, :technology_domain, :filing_date)
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "email": patent.email,
                "patent_title": patent.patent_title,
                "patent_number": patent.patent_number,
                "technology_domain": patent.technology_domain,
                "filing_date": patent.filing_date
            }
        )
        connection.commit()

    return {
        "message": "Patent added successfully"
    }


@router.get("/funding")
def get_all_funding():

    query = text("""
        SELECT * FROM funding_opportunities
    """)

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

    funding_list = []

    for row in result:
        funding_list.append({
            "id": row[0],
            "funding_name": row[1],
            "domain": row[2],
            "amount": row[3],
            "eligibility": row[4],
            "deadline": str(row[5])
        })

    return {
        "funding_opportunities": funding_list
    }

@router.get("/search-funding/{domain}")
def search_funding(domain: str):

    query = text("""
        SELECT * FROM funding_opportunities
        WHERE domain = :domain
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "domain": domain
            }
        ).fetchall()

    funding_list = []

    for row in result:
        funding_list.append({
            "id": row[0],
            "funding_name": row[1],
            "domain": row[2],
            "amount": row[3],
            "eligibility": row[4],
            "deadline": str(row[5])
        })

    return {
        "funding_opportunities": funding_list
    }


@router.put("/update-funding/{id}")
def update_funding(id: int, funding: FundingOpportunity):

    query = text("""
        UPDATE funding_opportunities
        SET
            funding_name = :funding_name,
            domain = :domain,
            amount = :amount,
            eligibility = :eligibility,
            deadline = :deadline
        WHERE id = :id
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "id": id,
                "funding_name": funding.funding_name,
                "domain": funding.domain,
                "amount": funding.amount,
                "eligibility": funding.eligibility,
                "deadline": funding.deadline
            }
        )
        connection.commit()

    return {
        "message": "Funding updated successfully"
    }


@router.delete("/delete-funding/{id}")
def delete_funding(id: int):

    query = text("""
        DELETE FROM funding_opportunities
        WHERE id = :id
    """)

    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "id": id
            }
        )
        connection.commit()

    return {
        "message": "Funding deleted successfully"
    }


@router.get("/matching-funding/{domain}")
def get_matching_funding(domain: str):

    query = text("""
        SELECT * FROM funding_opportunities
        WHERE LOWER(domain) = LOWER(:domain)
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"domain": domain}
        ).fetchall()

    funding_list = []

    for row in result:
        funding_list.append({
            "id": row[0],
            "funding_name": row[1],
            "domain": row[2],
            "amount": row[3],
            "eligibility": row[4],
            "deadline": str(row[5])
        })

    return {
        "matching_funding": funding_list
    }


@router.get("/publication-trends")
def publication_trends():

    query = text("""
        SELECT publication_year, COUNT(*) AS total
        FROM publications
        GROUP BY publication_year
        ORDER BY publication_year
    """)

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

    trends = []

    for row in result:
        trends.append({
            "year": row[0],
            "total_publications": row[1]
        })

    return {
        "publication_trends": trends
    }


@router.get("/dashboard-summary")
def dashboard_summary():

    with engine.connect() as connection:

        total_funding = connection.execute(
            text("SELECT COUNT(*) FROM funding_opportunities")
        ).scalar()

        total_publications = connection.execute(
            text("SELECT COUNT(*) FROM publications")
        ).scalar()

        total_patents = connection.execute(
            text("SELECT COUNT(*) FROM patents")
        ).scalar()

    return {
        "total_funding": total_funding,
        "total_publications": total_publications,
        "total_patents": total_patents
    }


@router.get("/generate-funding/{domain}")
def generate_funding(domain: str):

    with engine.connect() as connection:

        query = text("""
            SELECT *
            FROM funding_opportunities
            WHERE LOWER(domain) = LOWER(:domain)
        """)

        result = connection.execute(
            query,
            {"domain": domain}
        ).mappings().all()

    return {
        "generated_funding": result
    }


@router.get("/innovation-score")
def innovation_score():

    with engine.connect() as connection:

        publications = connection.execute(
            text("SELECT COUNT(*) FROM publications")
        ).scalar()

        patents = connection.execute(
            text("SELECT COUNT(*) FROM patents")
        ).scalar()

        funding = connection.execute(
            text("SELECT COUNT(*) FROM funding_opportunities")
        ).scalar()

    score = (publications * 10) + (patents * 20) + (funding * 5)

    return {
        "innovation_score": score
    }

@router.get("/patents")
def get_patents():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT * FROM patents")
        ).mappings().all()

    return {
        "patents": result
    }

@router.get("/funding")
def get_all_funding():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT * FROM funding_opportunities")
        ).fetchall()

    funding = []

    for row in result:

        funding.append({
            "id": row[0],
            "funding_name": row[1],
            "domain": row[2],
            "amount": row[3],
            "eligibility": row[4],
            "deadline": str(row[5])
        })

    return {
        "matching_funding": funding
    }