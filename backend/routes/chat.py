
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation, Message
from ..schemas import ChatRequest
from ..security import get_current_user

from llm.rag import MOSDACRAG


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# Load the RAG system once when the API starts.
rag = MOSDACRAG()


@router.post("/ask")
def ask_question(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ==================================================
    # 1. CHECK CONVERSATION OWNERSHIP
    # ==================================================

    # Identify the user using the verified JWT token.
    # Never trust a user_id supplied by the frontend.
    conversation = db.query(Conversation).filter(
        Conversation.chat_id == data.chat_id,
        Conversation.user_id == current_user.user_id,
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty",
        )

    # ==================================================
    # 2. LOAD PREVIOUS MESSAGES FOR THIS CHAT
    # ==================================================

    previous_messages = (
        db.query(Message)
        .filter(Message.chat_id == conversation.chat_id)
        .order_by(Message.message_id.desc())
        .limit(6)
        .all()
    )

    # Change newest-first order to chronological order.
    previous_messages.reverse()

    history = [
        {
            "question": item.input_query,
            "answer": item.output_response,
        }
        for item in previous_messages
    ]

    # ==================================================
    # 3. ASK YOUR EXISTING MOSDAC RAG CHATBOT
    # ==================================================

    try:
        result = rag.ask(
            question,
            history=history,
        )

        answer = result["answer"]
        sources = result.get("sources", [])

    except Exception:
        # Log the actual exception privately during development
        # if needed. Do not return API keys or secrets to users.
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="The MOSDAC assistant could not process this question",
        )

    # ==================================================
    # 4. SAVE QUESTION AND ANSWER IN POSTGRESQL
    # ==================================================

    message = Message(
        chat_id=conversation.chat_id,
        input_query=question,
        output_response=answer,
    )

    try:
        db.add(message)

        # Use the first question as the conversation title.
        if conversation.title == "New chat":
            conversation.title = question[:200]

        db.commit()
        db.refresh(message)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not save the chat history",
        )

    # ==================================================
    # 5. RETURN THE ANSWER TO THE FRONTEND
    # ==================================================

    return {
        "chat_id": conversation.chat_id,
        "message_id": message.message_id,
        "question": question,
        "answer": answer,
        "sources": sources,
    }
