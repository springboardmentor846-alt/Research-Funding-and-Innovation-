from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.dependencies import (
    get_current_user,
    get_db,
    require_role,
)
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister


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

    return {
    "access_token": access_token,
    "token_type": "bearer"
}

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