# db.py
# Database connection and session setup for Skillgap.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Environment variables will be moved to .env later.
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "skillgap"

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SQLAlchemy engine.
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production.
)

# Session factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Shared ORM base.
Base = declarative_base()


# FastAPI dependency for DB sessions.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import model modules after Base is defined so their tables register with Base.metadata.
# Do not call Base.metadata.create_all() in this file.
from app.models import user
from app.models import CV_entity
from app.models import JD_entity
from app.models import gap_snapshot
from app.models import normalised_entity
from app.models import course
from app.models import confirmed_skill