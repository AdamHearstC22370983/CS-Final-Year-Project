# This is the Database Connection file (db.py).
# It handles the connection between FastAPI and the PostgreSQL database.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Environment variables (will move to .env later)
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "skillgap"

# Construct full database URL
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True  # Set to False in production
)

# Create session maker for DB sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auto-create tables (development only)
# Import models here ONLY after Base is defined
from app.models import user, CV_entity, JD_entity, missing_entity, gap_snapshot
Base.metadata.create_all(bind=engine)
