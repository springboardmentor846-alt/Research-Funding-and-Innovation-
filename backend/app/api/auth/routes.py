from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest, RefreshTokenRequest
from app.crud.user import (
    create_user,
    get_user_by_email,
    create_password_reset_token,
    get_valid_reset_token,
    reset_user_password,
)
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_access_token, get_current_user, require_role
from app.core.limiter import limiter
from app.services.email_service import send_password_reset_email

router = APIRouter()


@router.post("/register")
@limiter.limit("5/minute")
def register(request: Request, user: UserRegister, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    return {"email": new_user.email, "message": "User registered successfully"}


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    refresh_token = create_refresh_token(data={"sub": db_user.email, "role": db_user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email": db_user.email,
        "name": db_user.name,
        "role": db_user.role,
    }
@router.post("/refresh")
def refresh_token_endpoint(payload: RefreshTokenRequest):
    if not payload.refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is required")

    token_data = decode_access_token(payload.refresh_token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(data={"sub": token_data.get("sub"), "role": token_data.get("role")})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, current_user.get("sub"))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": db_user.email, "name": db_user.name, "role": db_user.role}

@router.get("/researcher-only")
def researcher_route(current_user: dict = Depends(require_role(["researcher"]))):
    return {
        "message": "Welcome Researcher!",
        "email": current_user.get("sub")
    }


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Always returns a generic success message, whether or not the email exists,
    so this endpoint can't be used to enumerate registered accounts.
    """
    db_user = get_user_by_email(db, payload.email)

    if db_user:
        reset_token = create_password_reset_token(db, db_user.id)
        send_password_reset_email(db_user.email, reset_token.token)

    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_token = get_valid_reset_token(db, payload.token)

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    reset_user_password(db, reset_token, payload.new_password)

    return {"message": "Password has been reset successfully. You can now log in."}