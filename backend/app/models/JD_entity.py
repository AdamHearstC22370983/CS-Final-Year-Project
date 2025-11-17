# JD_entity.py
# Stores entities taken from a Job Description.

from sqlalchemy import Column, Integer, String
from app.models.db import Base

class JDEntity(Base):
    __tablename__ = "jd_entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
