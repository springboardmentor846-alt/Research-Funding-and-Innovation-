from app.models.user import User

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