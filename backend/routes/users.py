from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == data.email.lower()
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        username=data.username,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
    }