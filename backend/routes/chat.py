from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation, Message
from ..schemas import ChatRequest

from llm.rag import MOSDACRAG


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# Load RAG system once
rag = MOSDACRAG()


@router.post("/ask")
def ask_question(
    data: ChatRequest,
    db: Session = Depends(get_db)
):

    # ==================================================
    # CHECK USER
    # ==================================================

    user = db.query(User).filter(
        User.user_id == data.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    # ==================================================
    # CHECK CONVERSATION
    # ==================================================

    conversation = db.query(
        Conversation
    ).filter(
        Conversation.chat_id == data.chat_id,
        Conversation.user_id == data.user_id
    ).first()


    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )


    # ==================================================
    # SEND QUESTION TO RAG
    # ==================================================

    result = rag.ask(
        data.question
    )


    answer = result["answer"]

    sources = result["sources"]


    # ==================================================
    # SAVE MESSAGE
    # ==================================================

    message = Message(

        chat_id=data.chat_id,

        input_query=data.question,

        output_response=answer

    )

    db.add(message)

    db.commit()

    db.refresh(message)


    # ==================================================
    # RETURN RESPONSE
    # ==================================================

    return {

        "chat_id":
            data.chat_id,

        "message_id":
            message.message_id,

        "question":
            data.question,

        "answer":
            answer,

        "sources":
            sources

    }