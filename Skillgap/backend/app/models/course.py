from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from app.models.db import Base

# represents a course catalog entry
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    # Metadata used by search/recommendation/import
    type = Column(String, nullable=True)
    level = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    duration = Column(Float, nullable=True)

    # Skills
    skills = Column(JSONB, nullable=True)
    skills_norm = Column(JSONB, nullable=True)

    # Quality signals
    rating = Column(Float, nullable=True)
    nu_reviews = Column(Integer, nullable=True)
    enrollments = Column(Integer, nullable=True)

    # Optional import flags from the curated dataset
    has_rating = Column(Integer, nullable=True)
    has_subject = Column(Integer, nullable=True)
    has_no_enrol = Column(Integer, nullable=True)
