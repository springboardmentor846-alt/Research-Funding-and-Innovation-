from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:yukti%40123@localhost/funding_platform_db"

engine = create_engine(DATABASE_URL)