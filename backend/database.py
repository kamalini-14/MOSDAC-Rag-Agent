'''import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("DB_HOST     :", DB_HOST)
print("DB_PORT     :", DB_PORT)
print("DB_NAME     :", DB_NAME)
print("DB_USER     :", DB_USER)
print("DB_PASSWORD :", DB_PASSWORD)
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    echo=False
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()'''

# database.py


import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# Always load the .env file from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

required = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

missing = [
    key for key, value in required.items()
    if not value
]

if missing:
    raise RuntimeError(
        f"Missing database configuration: {', '.join(missing)}"
    )

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT
                current_database(),
                current_user,
                inet_server_port(),
                current_setting('search_path')
        """))
        print("Connected database details:", result.fetchone())

        result = connection.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'users'
            ORDER BY ordinal_position
        """))
        print("Users columns:", result.scalars().all())

