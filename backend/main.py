from fastapi import FastAPI

from .database import Base, engine

from .routes import users
from .routes import conversations
from .routes import chat


# ==================================================
# CREATE TABLES
# ==================================================

Base.metadata.create_all(
    bind=engine
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="MOSDAC RAG API",
    description="MOSDAC Knowledge Retrieval Chatbot API",
    version="1.0.0"
)


# ==================================================
# ROUTES
# ==================================================

app.include_router(
    users.router
)

app.include_router(
    conversations.router
)

app.include_router(
    chat.router
)


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {

        "message":
            "MOSDAC RAG API is running"

    }