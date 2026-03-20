# security.py
import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# Password hashing context.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# JWT config.
SECRET_KEY = os.getenv("SKILLGAP_SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Hash a plain-text password before storing it.
def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Password is required")

    password_bytes = len(password.encode("utf-8"))

    if password_bytes > 72:
        raise ValueError(
            f"Password is too long for bcrypt: {password_bytes} bytes"
        )

    return pwd_context.hash(password)


# Verify a plain-text password against a stored hash.
# Return False instead of crashing when legacy/bad password data is encountered.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or not isinstance(hashed_password, str):
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        # Stored password is not a recognised hash format.
        return False
    except ValueError:
        # Covers malformed hash strings and similar passlib parsing issues.
        return False


# Create a JWT access token for the authenticated user.
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Decode and validate a JWT token payload.
def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None