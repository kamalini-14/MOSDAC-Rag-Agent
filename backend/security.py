
import os
from datetime import datetime, timedelta, timezone

import jwt
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


# Load settings from your .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing from your .env file"
    )

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "60")
)

password_hasher = PasswordHash.recommended()

# Reads the Bearer token from the Authorization header.
bearer_scheme = HTTPBearer()


# ==========================================
# 1. HASH A PASSWORD
# ==========================================

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


# ==========================================
# 2. VERIFY A PASSWORD
# ==========================================

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(
        password,
        hashed_password
    )


# ==========================================
# 3. CREATE A JWT TOKEN
# ==========================================

def create_token(user_id: int) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expiry,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


# ==========================================
# 4. IDENTIFY THE LOGGED-IN USER
# ==========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])

    except (
        jwt.InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired login token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )

    return user
