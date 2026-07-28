from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.proposal import Proposal

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

router = APIRouter(tags=["Authentication"])


@router.get("/")
def home():
    return {
        "message": "Research Funding Platform API Running Successfully"
    }


# ---------------- REGISTER ---------------- #

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        organization=user.organization,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.full_name,
            "email": new_user.email,
            "organization": new_user.organization,
            "role": new_user.role
        }
    }


# ---------------- LOGIN ---------------- #

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ---------------- PROFILE ---------------- #

@router.get("/profile")
def get_profile(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "full_name": user.full_name,
        "email": user.email,
        "organization": user.organization,
        "role": user.role
    }


# ---------------- UPDATE PROFILE ---------------- #

@router.put("/profile")
def update_profile(
    profile: dict,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.full_name = profile.get(
        "full_name",
        user.full_name
    )

    user.organization = profile.get(
        "organization",
        user.organization
    )

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile Updated Successfully"
    }


# ---------------- CHANGE PASSWORD ---------------- #

@router.put("/profile/password")
def change_password(
    passwords: dict,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        passwords["old_password"],
        user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current Password Incorrect"
        )

    user.password = hash_password(
        passwords["new_password"]
    )

    db.commit()

    return {
        "message": "Password Updated Successfully"
    }


# ---------------- DELETE ACCOUNT ---------------- #

@router.delete("/profile")
def delete_profile(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.query(ResearchProfile).filter(
        ResearchProfile.user_id == user.id
    ).delete()

    db.query(Proposal).filter(
        Proposal.user_id == user.id
    ).delete()

    db.delete(user)

    db.commit()

    return {
        "message": "Account Deleted Successfully"
    }