from pydantic import BaseModel, EmailStr
# Pydantic schema for user creation to bypass bcrypt >72 bytes issue
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
