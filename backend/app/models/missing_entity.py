# missing_entity.py

# Stores the required job entities that do NOT appear in the CV.
# This forms the core of the Skillgap calculation.

from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.db import Base

class MissingEntity(Base):
    __tablename__ = "missing_entities"

    id = Column(Integer, primary_key=True)

    jd_entity_id = Column(Integer, ForeignKey("jd_entities.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    entity_name = Column(String, nullable=False)
