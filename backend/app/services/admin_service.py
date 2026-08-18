from app.models.user import User


# =========================================================
# ALLOWED ROLES
# =========================================================

ALLOWED_ROLES = {
    "Researcher",
    "Investor",
    "Startup Founder",
    "University",
    "Funding Agency",
    "Industry Partner",
    "Admin"
}


# =========================================================
# VERIFY USER
# =========================================================

def verify_user(db, user_id):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    user.is_verified = True

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# GET ALL USERS
# =========================================================

def get_all_users(db):

    users = (
        db.query(User)
        .order_by(User.id.asc())
        .all()
    )

    return users


# =========================================================
# GET USER BY ID
# =========================================================

def get_user_by_id(
    db,
    user_id
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    return user


# =========================================================
# CHANGE USER ROLE
# =========================================================

def change_user_role(
    db,
    user_id,
    new_role
):

    if new_role not in ALLOWED_ROLES:
        raise ValueError(
            "Invalid role"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    user.role = new_role

    db.commit()
    db.refresh(user)

    return user


# =========================================================
# PLATFORM ANALYTICS
# =========================================================

def get_platform_analytics(db):

    total_users = (
        db.query(User)
        .count()
    )

    verified_users = (
        db.query(User)
        .filter(
            User.is_verified == True
        )
        .count()
    )

    pending_users = (
        db.query(User)
        .filter(
            User.is_verified == False
        )
        .count()
    )

    admin_count = (
        db.query(User)
        .filter(
            User.role == "Admin"
        )
        .count()
    )

    researcher_count = (
        db.query(User)
        .filter(
            User.role == "Researcher"
        )
        .count()
    )

    investor_count = (
        db.query(User)
        .filter(
            User.role == "Investor"
        )
        .count()
    )

    startup_count = (
        db.query(User)
        .filter(
            User.role == "Startup Founder"
        )
        .count()
    )

    university_count = (
        db.query(User)
        .filter(
            User.role == "University"
        )
        .count()
    )

    funding_agency_count = (
        db.query(User)
        .filter(
            User.role == "Funding Agency"
        )
        .count()
    )

    industry_partner_count = (
        db.query(User)
        .filter(
            User.role == "Industry Partner"
        )
        .count()
    )

    return {
        "total_users": total_users,

        "verified_users": verified_users,

        "pending_users": pending_users,

        "roles": {
            "Admin": admin_count,
            "Researcher": researcher_count,
            "Investor": investor_count,
            "Startup Founder": startup_count,
            "University": university_count,
            "Funding Agency": funding_agency_count,
            "Industry Partner": industry_partner_count
        }
    }