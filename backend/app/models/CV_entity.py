
# CV_entity.py

# Stores extracted entities from a user's CV.
# Entities consist of skills, experience, qualifications, etc.

#Linked to a User through user_id.

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.db import Base

class CVEntity(Base):
    __tablename__ = "cv_entities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    entity_name = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)

    user = relationship("User")
