from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin
from app.crud.user import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_access_token, get_current_user, require_role
from app.core.limiter import limiter

router = APIRouter()


@router.get("/test")
def test_auth():
    return {"message": "Auth API Working"}


@router.post("/register")
@limiter.limit("5/minute")
def register(request: Request, user: UserRegister, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db, user)

    return {
        "message": "User registered successfully",
        "email": new_user.email
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):

    db_user = get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": db_user.email, "role": db_user.role}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email": db_user.email,
        "role": db_user.role
    }


@router.post("/refresh")
def refresh_token(payload: dict):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    decoded = decode_access_token(token)
    if decoded is None or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(
        data={"sub": decoded.get("sub"), "role": decoded.get("role")}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user.get("sub"),
        "role": current_user.get("role")
    }


@router.get("/researcher-only")
def researcher_route(current_user: dict = Depends(require_role(["researcher"]))):
    return {
        "message": "Welcome Researcher!",
        "email": current_user.get("sub")
    }