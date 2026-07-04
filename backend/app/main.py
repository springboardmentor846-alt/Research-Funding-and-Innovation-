from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Research Funding Platform Backend is running"}

@app.get("/db-test")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "message": "Database connection successful",
            "result": result.scalar()
        }