from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.technology import Technology
from app.schemas.technology import (
    TechnologyCreate,
    TechnologyUpdate,
    TechnologyResponse,
)

router = APIRouter(
    prefix="/technologies",
    tags=["Technology Intelligence"]
)

# ==========================================================
# Create Technology
# ==========================================================
@router.post("/", response_model=TechnologyResponse)
def create_technology(
    technology: TechnologyCreate,
    db: Session = Depends(get_db)
):
    new_technology = Technology(**technology.model_dump())

    db.add(new_technology)
    db.commit()
    db.refresh(new_technology)

    return new_technology


# ==========================================================
# Get All Technologies
# ==========================================================
@router.get("/", response_model=list[TechnologyResponse])
def get_all_technologies(
    db: Session = Depends(get_db)
):
    return db.query(Technology).all()


# ==========================================================
# Search by Category
# ==========================================================
@router.get("/search/category", response_model=list[TechnologyResponse])
def search_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.category.ilike(f"%{category}%")
    ).all()


# ==========================================================
# Search by Maturity Level
# ==========================================================
@router.get("/search/maturity", response_model=list[TechnologyResponse])
def search_by_maturity(
    maturity_level: str,
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.maturity_level.ilike(f"%{maturity_level}%")
    ).all()


# ==========================================================
# High Growth Technologies
# ==========================================================
@router.get("/search/high-growth", response_model=list[TechnologyResponse])
def high_growth_technologies(
    min_score: float = 80,
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.growth_score >= min_score
    ).all()


# ==========================================================
# High Adoption Technologies
# ==========================================================
@router.get("/search/high-adoption", response_model=list[TechnologyResponse])
def high_adoption_technologies(
    min_rate: float = 70,
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.adoption_rate >= min_rate
    ).all()


# ==========================================================
# Top Technologies by Growth Score
# ==========================================================
@router.get("/top-growth", response_model=list[TechnologyResponse])
def top_growth_technologies(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    return db.query(Technology).order_by(
        Technology.growth_score.desc()
    ).limit(limit).all()


# ==========================================================
# Technology Statistics
# ==========================================================
@router.get("/statistics")
def technology_statistics(
    db: Session = Depends(get_db)
):
    technologies = db.query(Technology).all()

    total = len(technologies)

    if total == 0:
        return {
            "total_technologies": 0,
            "average_growth_score": 0,
            "average_adoption_rate": 0
        }

    avg_growth = sum(
        t.growth_score for t in technologies
    ) / total

    avg_adoption = sum(
        t.adoption_rate for t in technologies
    ) / total

    return {
        "total_technologies": total,
        "average_growth_score": round(avg_growth, 2),
        "average_adoption_rate": round(avg_adoption, 2)
    }


# ==========================================================
# Category Analytics
# ==========================================================
@router.get("/analytics/category")
def category_analytics(
    db: Session = Depends(get_db)
):
    analytics = (
        db.query(
            Technology.category,
            func.count(Technology.id).label("count")
        )
        .group_by(Technology.category)
        .all()
    )

    return [
        {
            "category": item.category,
            "count": item.count
        }
        for item in analytics
    ]


# ==========================================================
# Get Technology by ID
# ==========================================================
@router.get("/{technology_id}", response_model=TechnologyResponse)
def get_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    technology = db.query(Technology).filter(
        Technology.id == technology_id
    ).first()

    if not technology:
        raise HTTPException(
            status_code=404,
            detail="Technology not found"
        )

    return technology


# ==========================================================
# Update Technology
# ==========================================================
@router.put("/{technology_id}", response_model=TechnologyResponse)
def update_technology(
    technology_id: int,
    updated_technology: TechnologyUpdate,
    db: Session = Depends(get_db)
):
    technology = db.query(Technology).filter(
        Technology.id == technology_id
    ).first()

    if not technology:
        raise HTTPException(
            status_code=404,
            detail="Technology not found"
        )

    for key, value in updated_technology.model_dump().items():
        setattr(technology, key, value)

    db.commit()
    db.refresh(technology)

    return technology


# ==========================================================
# Delete Technology
# ==========================================================
@router.delete("/{technology_id}")
def delete_technology(
    technology_id: int,
    db: Session = Depends(get_db)
):
    technology = db.query(Technology).filter(
        Technology.id == technology_id
    ).first()

    if not technology:
        raise HTTPException(
            status_code=404,
            detail="Technology not found"
        )

    db.delete(technology)
    db.commit()

    return {
        "message": "Technology deleted successfully"
    }