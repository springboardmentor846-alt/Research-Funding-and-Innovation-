from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

SECRET_KEY = "research_funding_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401,
                                detail="Invalid Token")

    except Exception:
        raise HTTPException(status_code=401,
                            detail="Invalid Token")

    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise HTTPException(status_code=401,
                            detail="User not found")

    return user

def require_role(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    allowed_roles = {role.lower() for role in allowed_roles}
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role.lower() not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access Denied"
            )
        return current_user

    return role_checker
