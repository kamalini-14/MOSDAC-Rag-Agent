from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation
from ..schemas import ConversationCreate


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post("/")
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == data.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    conversation = Conversation(
        user_id=data.user_id
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return {

        "message":
            "Conversation created successfully",

        "chat_id":
            conversation.chat_id,

        "user_id":
            conversation.user_id
    }