# course.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.models.db import Base

# Course model representing the courses table in the database, with fields for course details and skills.
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    level = Column(String, nullable=True)
    duration = Column(Float, nullable=True)
    # Raw skills as ingested (provider/Kaggle phrasing)
    skills = Column(JSONB, nullable=True)
    # NEW: ESCO-canonical skills (preferred labels)
    skills_norm = Column(JSONB, nullable=True)
    rating = Column(Float, nullable=True)
    nu_reviews = Column(Integer, nullable=True)
    enrollments = Column(Integer, nullable=True)
