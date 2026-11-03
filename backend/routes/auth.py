
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserLogin, TokenResponse, UserResponse
from ..security import verify_password, create_token
from ..security import get_current_user
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == data.email.lower())
        .first()
    )

    if user is None or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_token(user.user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user