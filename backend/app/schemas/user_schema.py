from pydantic import BaseModel, EmailStr
# Pydantic schema for user creation to bypass bcrypt >72 bytes issue
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Used when signing in
# The identifier can be either a username or an email.
class UserLogin(BaseModel):
    identifier: str
    password : str

# Function used for changing account password
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str