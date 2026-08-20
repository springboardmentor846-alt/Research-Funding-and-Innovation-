from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.role import Role
from app.models.user import User


def main():
    print("InnovFund administrator provisioning")
    print("-----------------------------------")

    full_name = input("Administrator full name: ").strip()
    email = input("Administrator email: ").strip().lower()
    password = getpass("Administrator password (min 8 chars): ")

    if len(full_name) < 2:
        raise SystemExit("Full name must contain at least 2 characters.")

    if len(password) < 8:
        raise SystemExit("Password must contain at least 8 characters.")

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            raise SystemExit(
                "A user with this email already exists. "
                "Use the administrator console to manage the account."
            )

        admin_role = db.scalar(
            select(Role).where(Role.name == "administrator")
        )

        if admin_role is None:
            raise SystemExit(
                "The administrator role does not exist. "
                "Run scripts/seed_roles.py first."
            )

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role_id=admin_role.id,
            is_active=True,
        )

        db.add(admin)
        db.commit()

    print("Administrator account created successfully.")


if __name__ == "__main__":
    main()
