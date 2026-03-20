from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.db import Base
# ConfirmedSkill.py
# Stores skills that a user has confirmed as part of their profile.
class ConfirmedSkill(Base):
    __tablename__ = "confirmed_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    skill_name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")