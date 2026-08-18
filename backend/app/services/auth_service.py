from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import hash_password


# Roles that users are allowed to select during registration
REGISTRATION_ROLES = {
    "Researcher",
    "Investor",
    "Startup Founder",
    "University",
    "Funding Agency",
    "Industry Partner",
}


def create_user(
    db: Session,
    user_data
):

    # =========================================================
    # CHECK EXISTING EMAIL
    # =========================================================

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:
        return None

    # =========================================================
    # VALIDATE ROLE
    # =========================================================

    requested_role = (
        user_data.role.strip()
        if user_data.role
        else ""
    )

    if requested_role not in REGISTRATION_ROLES:

        raise ValueError(
            "Invalid registration role. "
            "Admin accounts can only be created by an administrator."
        )

    # =========================================================
    # CREATE USER
    # =========================================================

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hash_password(
            user_data.password
        ),
        role=requested_role,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user