from app.database.db import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


db = SessionLocal()

try:
    admin_email = "admin@innobridge.ai"
    admin_password = "Admin@12345"

    existing_admin = (
        db.query(User)
        .filter(User.email == admin_email)
        .first()
    )

    if existing_admin:
        print("Admin account already exists.")

        existing_admin.role = "Admin"
        existing_admin.is_verified = True

        db.commit()

        print("Admin account updated successfully.")

    else:
        admin = User(
            full_name="InnoBridge Admin",
            email=admin_email,
            password=hash_password(admin_password),
            role="Admin",
            is_verified=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("Admin account created successfully.")
        print("Admin ID:", admin.id)

finally:
    db.close()