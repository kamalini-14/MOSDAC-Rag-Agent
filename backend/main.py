from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    auth.router
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