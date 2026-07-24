import sys
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
import app.models.research_profile  # noqa: F401


def main():
    Base.metadata.create_all(bind=engine)

    if len(sys.argv) >= 4:
        email, full_name, password = sys.argv[1], sys.argv[2], sys.argv[3]
    else:
        email = input("Admin email: ").strip()
        full_name = input("Full name: ").strip()
        password = input("Password: ").strip()

    if not email or not password:
        print("Email and password are required.")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = UserRole.ADMIN
            db.commit()
            print(f"Existing user '{email}' promoted to ADMIN.")
        else:
            user = User(
                email=email,
                full_name=full_name or "Administrator",
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
                original_role=UserRole.ADMIN,
            )
            db.add(user)
            db.commit()
            print(f"Admin account created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
