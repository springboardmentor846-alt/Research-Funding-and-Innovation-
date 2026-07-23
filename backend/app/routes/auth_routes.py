from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate
from app.schemas.login_schema import LoginRequest

from app.services.auth_service import create_user
from app.services.login_service import authenticate_user

from app.database.db import get_db
from app.utils.jwt_handler import create_access_token
from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/")
def auth_test():
    return {
        "message": "Authentication Module Working"
    }


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        created_user = create_user(db, user)

        if not created_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        return {
            "message": "User Registered Successfully"
        }

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    if user == "NOT_VERIFIED":
        raise HTTPException(
            status_code=403,
            detail="Account Not Verified"
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    
    access_token = create_access_token(
    {
        "id": user.id,
        "sub": user.email,
        "role": user.role
    }
)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }


@router.get("/profile")
def profile(
    current_user=Depends(get_current_user)
):
    return {
        "message": "Protected Route Access Granted",
        "user": current_user
    }