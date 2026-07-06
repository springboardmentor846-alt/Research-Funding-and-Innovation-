from sqlalchemy import select

from app.database import SessionLocal
from app.models.role import Role


ROLE_NAMES = [
    "researcher",
    "startup_founder",
    "innovation_manager",
    "administrator",
]


def seed_roles():
    with SessionLocal() as db:
        for role_name in ROLE_NAMES:
            existing_role = db.scalar(
                select(Role).where(Role.name == role_name)
            )

            if existing_role is None:
                db.add(Role(name=role_name))

        db.commit()

    print("Roles seeded successfully")


if __name__ == "__main__":
    seed_roles()