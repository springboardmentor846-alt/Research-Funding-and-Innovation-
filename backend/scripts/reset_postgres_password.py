from sqlalchemy import text

from app.database import engine


NEW_PASSWORD = "PostgreSql@06"


with engine.begin() as connection:
    connection.execute(
        text(f"ALTER USER postgres WITH PASSWORD '{NEW_PASSWORD}'")
    )

print("PostgreSQL password reset successfully")