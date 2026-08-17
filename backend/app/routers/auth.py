from datetime import datetime, timedelta, timezone
import jwt


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
    create_password_reset_token,
    hash_password_reset_token,

)
from app.dependencies import (
    get_current_user,
    get_db,
    require_role,
)
from app.models.role import Role
from app.models.user import User
from app.models.collaboration_request import CollaborationRequest
from app.models.organization_information import OrganizationInformation
from app.models.patent import Patent
from app.models.publication import Publication
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.researcher_imported_publication import ResearcherImportedPublication
from app.models.research_profile import ResearchProfile
from app.models.startup import Startup
from app.models.technology_area import TechnologyArea
from app.models.password_reset_token import PasswordResetToken
from app.config import settings
from app.schemas.user import (
    UserLogin,
    UserRegister,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    role = db.scalar(
        select(Role).where(Role.name == user_data.role)
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role_id=role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": role.name
    }

@router.post("/login")
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.email == login_data.email)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    role = db.get(Role, user.role_id)
    access_token = create_access_token(
    user_id=user.id,
    role=role.name
    )

    refresh_token = create_refresh_token(
    user_id=user.id
)

    return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer"
}


@router.post("/refresh")
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = decode_token(
            token_data.refresh_token
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = int(payload["sub"])

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    role = db.get(Role, user.role_id)

    access_token = create_access_token(
        user_id=user.id,
        role=role.name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == request.email))

    message = {"message": "If an account exists with this email, a password reset link has been sent."}

    if user is None:
        return message

    existing_tokens = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    ).all()

    now = datetime.now(timezone.utc)
    for old_token in existing_tokens:
        old_token.used_at = now

    raw_token = create_password_reset_token()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_password_reset_token(raw_token),
        expires_at=now + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
    )
    db.add(reset_token)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    from app.services.email_service import send_password_reset_email
    try:
        send_password_reset_email(user.email, reset_link)
    except Exception:
        reset_token.used_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to send the password reset email. Please try again later.",
        )

    return message


@router.delete("/account")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete the authenticated user's account and owned data."""

    user_id = current_user.id

    # Remove records that reference the user directly.
    db.query(CollaborationRequest).filter(
        (CollaborationRequest.sender_user_id == user_id)
        | (CollaborationRequest.recipient_user_id == user_id)
    ).delete(synchronize_session=False)

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id
    ).delete(synchronize_session=False)

    startup = db.scalar(select(Startup).where(Startup.user_id == user_id))
    if startup is not None:
        db.delete(startup)

    profile = db.scalar(
        select(ResearchProfile).where(ResearchProfile.user_id == user_id)
    )
    if profile is not None:
        profile_id = profile.id

        # These tables do not all declare ON DELETE CASCADE, so remove their
        # records explicitly before removing the research profile.
        db.query(OrganizationInformation).filter(
            OrganizationInformation.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(ResearchDomain).filter(
            ResearchDomain.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(ResearchKeyword).filter(
            ResearchKeyword.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(TechnologyArea).filter(
            TechnologyArea.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(ResearcherImportedPublication).filter(
            ResearcherImportedPublication.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(Patent).filter(
            Patent.research_profile_id == profile_id
        ).delete(synchronize_session=False)
        db.query(Publication).filter(
            Publication.research_profile_id == profile_id
        ).delete(synchronize_session=False)

        db.delete(profile)

    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_password_reset_token(request.token)
    reset_token = db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )

    if reset_token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset link")

    now = datetime.now(timezone.utc)
    if reset_token.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This password reset link has already been used")
    if reset_token.expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This password reset link has expired")

    user = db.get(User, reset_token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password reset request")

    user.hashed_password = hash_password(request.new_password)
    reset_token.used_at = now
    db.commit()

    return {"message": "Password reset successfully"}


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = db.get(Role, current_user.role_id)

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": role.name,
        "is_active": current_user.is_active
    }

@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_role("administrator")
    )
):
    return {
        "message": "Administrator access granted",
        "user_id": current_user.id
    }