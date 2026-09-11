from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    user = User(
        username=user_data.username
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message": "User created successfully",
        "user_id": user.user_id,
        "username": user.username
    }