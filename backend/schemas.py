'''from pydantic import BaseModel


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

    question: str'''

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ConversationCreate(BaseModel):
    title: str = "New chat"


class ChatRequest(BaseModel):
    chat_id: int
    question: str = Field(min_length=1)


class MessageResponse(BaseModel):
    message_id: int
    chat_id: int
    input_query: str
    output_response: str

    model_config = {"from_attributes": True}
