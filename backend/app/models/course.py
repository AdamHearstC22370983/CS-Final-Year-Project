from sqlalchemy import Column, Integer, String, Text, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.models.db import Base


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("url", name="uq_courses_url"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # identity/display
    url = Column(String, nullable=False, index=True)
    course_name = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)        # e.g., "coursera", "edx_courses", "edx_programs"
    organization = Column(String, nullable=True, index=True)     # uni/partner
    type = Column(String, nullable=True, index=True)             # course/program/etc.

    # recommender fields
    level = Column(String, nullable=True, index=True)
    subject = Column(String, nullable=True, index=True)
    duration = Column(Float, nullable=True)                      # hours proxy
    rating = Column(Float, nullable=True)
    nu_reviews = Column(Integer, nullable=True)
    enrollments = Column(Integer, nullable=True)

    # text + tags
    description = Column(Text, nullable=True)
    skills = Column(JSONB, nullable=False, default=list)         # list[str]

    # internal flags (optional but useful)
    has_rating = Column(Integer, nullable=True)
    has_subject = Column(Integer, nullable=True)
    has_no_enrol = Column(Integer, nullable=True)