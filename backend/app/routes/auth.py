from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import (
    verify_token,
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    PasswordUpdate,
)
from app.models.research_profile import ResearchProfile
from app.models.proposal import Proposal

router = APIRouter(
    tags=["Authentication"]
)


@router.get("/")
def home():
    return {
        "message": "Research Funding Platform API Running Successfully"
    }


@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        organization=user.organization,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/profile")
def profile(
    token: dict = Depends(verify_token)
):

    return {
        "message": "Profile Access Granted",
        "user": token
    }


@router.put("/profile")
def update_profile(
    profile: UserUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    user.full_name = profile.full_name
    user.organization = profile.organization

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile Updated Successfully",
        "user": {
            "full_name": user.full_name,
            "email": user.email,
            "organization": user.organization,
            "role": user.role
        }
    }


@router.put("/profile/password")
def change_password(
    password: PasswordUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    if not verify_password(
        password.old_password,
        user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Old Password is Incorrect"
        )

    user.password = hash_password(
        password.new_password
    )

    db.commit()

    return {
        "message": "Password Changed Successfully"
    }


@router.delete("/profile")
def delete_profile(
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
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