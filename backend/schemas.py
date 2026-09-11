from pydantic import BaseModel


# ==================================================
# CREATE USER
# ==================================================

class UserCreate(BaseModel):

    username: str


# ==================================================
# CREATE CONVERSATION
# ==================================================

class ConversationCreate(BaseModel):

    user_id: int


# ==================================================
# CHAT REQUEST
# ==================================================

class ChatRequest(BaseModel):

    user_id: int

    chat_id: int

    question: str