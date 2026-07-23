from fastapi import APIRouter, Depends

from app.utils.auth_dependency import get_current_user
from app.utils.role_checker import role_required
from app.services.admin_service import verify_user
from sqlalchemy.orm import Session
from app.database.db import get_db
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_profile(
    current_user=Depends(get_current_user)
):
    return {
        "message": "User Profile",
        "user": current_user
    }
@router.get("/admin-only")
def admin_only(
    current_user=Depends(get_current_user)
):

    role_required(
        ["Admin"]
    )(current_user)

    return {
        "message": "Welcome Admin"
    }
@router.get("/researcher-only")
def researcher_only(
    current_user=Depends(get_current_user)
):

    role_required(
        ["Researcher", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Researcher"
    }
@router.get("/investor-only")
def investor_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Investor", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Investor"
    }
@router.get("/startup-only")
def startup_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Startup Founder", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Startup Founder"
    }
@router.get("/university-only")
def university_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["University", "Admin"]
    )(current_user)

    return {
        "message": "Welcome University"
    }
@router.get("/funding-only")
def funding_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Funding Agency", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Funding Agency"
    }
@router.get("/industry-only")
def industry_only(
    current_user=Depends(get_current_user)
):
    role_required(
        ["Industry Partner", "Admin"]
    )(current_user)

    return {
        "message": "Welcome Industry Partner"
    }
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
        return {
            "message": "User Not Found"
        }

    return {
        "message": "User Verified Successfully",
        "user_id": user.id,
        "email": user.email,
        "is_verified": user.is_verified
    }