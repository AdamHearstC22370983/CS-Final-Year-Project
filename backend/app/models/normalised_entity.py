from sqlalchemy import Column, Integer, String, Text
from app.models.db import Base

class NormalisedEntity(Base):
    __tablename__ = "normalised_entities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    original = Column(String, nullable=False)
    normalised = Column(String, nullable=False)
    uri = Column(String, nullable=True)
    source = Column(String, nullable=False)  # ESCO or RAW
    entity_type = Column(String, nullable=False)
