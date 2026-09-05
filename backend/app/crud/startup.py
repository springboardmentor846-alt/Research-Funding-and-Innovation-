from sqlalchemy.orm import Session
from app.models.startup import Startup
from app.schemas.startup import StartupCreate, StartupUpdate


def get_startup_by_user_id(db: Session, user_id: int):
    return db.query(Startup).filter(Startup.user_id == user_id).first()


def get_startup_by_id(db: Session, startup_id: int):
    return db.query(Startup).filter(Startup.id == startup_id).first()


def create_startup(db: Session, user_id: int, data: StartupCreate):
    new_startup = Startup(user_id=user_id, **data.model_dump())
    db.add(new_startup)
    db.commit()
    db.refresh(new_startup)
    return new_startup


def update_startup(db: Session, startup: Startup, data: StartupUpdate):
    for field, value in data.model_dump().items():
        setattr(startup, field, value)
    db.commit()
    db.refresh(startup)
    return startup