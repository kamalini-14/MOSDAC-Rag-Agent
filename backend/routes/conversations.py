
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation, Message
from ..schemas import ConversationCreate
from ..security import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/")
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    title = (data.title or "New chat").strip() or "New chat"

    conversation = Conversation(
        user_id=current_user.user_id,
        title=title[:200],
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "message": "Conversation created successfully",
        "chat_id": conversation.chat_id,
        "user_id": conversation.user_id,
        "title": conversation.title,
    }


@router.get("/")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return [
        {
            "chat_id": item.chat_id,
            "title": item.title,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in conversations
    ]


@router.get("/{chat_id}/messages")
def get_conversation_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.chat_id == chat_id,
            Conversation.user_id == current_user.user_id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.message_id.asc())
        .all()
    )

    return [
        {
            "message_id": item.message_id,
            "chat_id": item.chat_id,
            "question": item.input_query,
            "answer": item.output_response,
            "created_at": item.created_at,
        }
        for item in messages
    ]
