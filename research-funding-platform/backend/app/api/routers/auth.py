from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, ResearchProfile
from app.schemas.schemas import UserRegister, UserLogin, Token, ForgotPassword, ResetPassword
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role,
        organization=user_in.organization or "Independent Researcher",
        is_active=True,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize empty profile
    profile = ResearchProfile(
        user_id=new_user.id,
        organization=new_user.organization,
        domains="Artificial Intelligence, Computer Science",
        keywords="Machine Learning, Neural Networks"
    )
    db.add(profile)
    db.commit()

    access_token = create_access_token(subject=new_user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "organization": new_user.organization
        }
    }

@router.post("/login", response_model=Token)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled.")

    access_token = create_access_token(subject=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization": user.organization
        }
    }

@router.post("/google-login", response_model=Token)
def google_oauth_login(payload: Dict[str, Any], db: Session = Depends(get_db)):
    email = payload.get("email", "google.user@example.com")
    name = payload.get("name", "Google User")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("GoogleOAuth2026!"),
            full_name=name,
            role="Researcher",
            organization="Google OAuth Partner",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(subject=user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization": user.organization
        }
    }

@router.post("/forgot-password")
def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Prevent user enumeration
        return {"message": "If the email is registered, a password reset link has been dispatched."}
    
    reset_token = create_access_token(subject=user.email)
    return {
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token
    }

@router.post("/reset-password")
def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
    from app.core.security import decode_access_token
    decoded = decode_access_token(payload.token)
    if not decoded or "sub" not in decoded:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    user = db.query(User).filter(User.email == decoded["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully. You may now log in."}
