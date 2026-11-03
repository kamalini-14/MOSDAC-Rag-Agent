'''from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from .database import Base


# ==================================================
# USER
# ==================================================

class User(Base):

    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        nullable=False
    )


# ==================================================
# CONVERSATION
# ==================================================

class Conversation(Base):

    __tablename__ = "conversations"

    chat_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )


# ==================================================
# MESSAGE
# ==================================================

class Message(Base):

    __tablename__ = "messages"

    message_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("conversations.chat_id"),
        nullable=False
    )

    input_query = Column(
        Text,
        nullable=False
    )

    output_response = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )'''

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from .database import Base


# USER TABLE
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Store a secure password hash, never the plain password.
    password_hash = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# CONVERSATION TABLE
class Conversation(Base):
    __tablename__ = "conversations"

    chat_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False, default="New chat")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# MESSAGE TABLE
class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)

    chat_id = Column(
        Integer,
        ForeignKey("conversations.chat_id"),
        nullable=False,
        index=True,
    )

    input_query = Column(Text, nullable=False)
    output_response = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
