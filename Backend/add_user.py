from models import User
from database import engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = User(
    name="Admin",
    email="admin@gmail.com",
    password="1234",
    role="Admin"
)

db.add(user)
db.commit()
db.close()

print("User Added Successfully")