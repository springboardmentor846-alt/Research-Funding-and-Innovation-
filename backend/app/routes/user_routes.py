from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils.auth_dependency import get_current_user
from app.utils.role_checker import role_required

from app.services.admin_service import (
    verify_user,
    get_all_users,
    get_user_by_id,
    change_user_role,
    get_platform_analytics
)

from app.database.db import get_db


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# CURRENT USER
# =========================================================

@router.get("/me")
def get_my_profile(
    current_user=Depends(get_current_user)
):
    return {
        "message": "User Profile",
        "user": current_user
    }


# =========================================================
# ROLE TEST ENDPOINTS
# =========================================================

@router.get("/admin-only")
def admin_only(
    current_user=Depends(get_current_user)
):
    role_required(["Admin"])(current_user)

    return {
        "message": "Welcome Admin",
        "role": current_user["role"]
    }


@router.get("/researcher-only")
def researcher_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Researcher", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Researcher",
        "role": current_user["role"]
    }


@router.get("/investor-only")
def investor_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Investor", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Investor",
        "role": current_user["role"]
    }


@router.get("/startup-only")
def startup_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Startup Founder", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Startup Founder",
        "role": current_user["role"]
    }


@router.get("/university-only")
def university_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["University", "Admin"]
    )(current_user)

    return {
        "message": "Welcome University",
        "role": current_user["role"]
    }


@router.get("/funding-only")
def funding_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Funding Agency", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Funding Agency",
        "role": current_user["role"]
    }


@router.get("/industry-only")
def industry_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Industry Partner", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Industry Partner",
        "role": current_user["role"]
    }


# =========================================================
# ADMIN - VERIFY USER
# =========================================================

@router.put("/verify-user/{user_id}")
def verify_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(["Admin"])(current_user)

    user = verify_user(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {
        "message": "User Verified Successfully",
        "user_id": user.id,
        "email": user.email,
        "is_verified": user.is_verified
    }


# =========================================================
# ADMIN - GET ALL USERS
# =========================================================

@router.get("/admin/users")
def get_users_for_admin(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(["Admin"])(current_user)

    users = get_all_users(db)

    return {
        "count": len(users),
        "users": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "is_verified": user.is_verified
            }
            for user in users
        ]
    }


# =========================================================
# ADMIN - GET SINGLE USER
# =========================================================

@router.get("/admin/users/{user_id}")
def get_single_user_for_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(["Admin"])(current_user)

    user = get_user_by_id(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_verified": user.is_verified
    }


# =========================================================
# ADMIN - CHANGE USER ROLE
# =========================================================

@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(["Admin"])(current_user)

    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot change their own role"
        )

    try:

        user = change_user_role(
            db,
            user_id,
            new_role
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {
        "message": "User Role Updated Successfully",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified
        }
    }


# =========================================================
# ADMIN - PLATFORM ANALYTICS
# =========================================================

@router.get("/admin/analytics")
def platform_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(["Admin"])(current_user)

    return get_platform_analytics(db)