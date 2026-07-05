from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

router = APIRouter()


@router.get("/test")
def test():
    return {"message": "User router is working!"}


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully!",
        "id": new_user.id
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        return {"message": "Invalid email or password"}

    if not verify_password(user.password, db_user.password):
        return {"message": "Invalid email or password"}

    token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }