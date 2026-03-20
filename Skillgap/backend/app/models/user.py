# user.py
# User requires the following fields:
# - username
# - email
# - hashed password
#Do NOT store plain passwords — only hashed_password.

from sqlalchemy import Column, Integer, String
from app.models.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Login fields
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Store ONLY the hashed password
    hashed_password = Column(String, nullable=False)
