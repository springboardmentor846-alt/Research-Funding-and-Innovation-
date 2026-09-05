import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user import UserRegister
from app.core.security import hash_password

RESET_TOKEN_EXPIRE_MINUTES = 30


def create_user(db: Session, user: UserRegister):
    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_password_reset_token(db: Session, user_id: int) -> PasswordResetToken:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token


def get_valid_reset_token(db: Session, token: str):
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token)
        .first()
    )
    if not reset_token:
        return None
    if reset_token.used:
        return None
    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    return reset_token


def reset_user_password(db: Session, reset_token: PasswordResetToken, new_password: str):
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        return None
    user.password = hash_password(new_password)
    reset_token.used = True
    db.commit()
    db.refresh(user)
    return user