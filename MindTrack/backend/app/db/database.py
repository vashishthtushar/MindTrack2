import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# app/db/database.py
"""
Database setup for MindTrack.

Provides:
- Base: SQLAlchemy declarative base for models.
- engine: SQLAlchemy Engine created from DATABASE_URL (defaults to sqlite:///./mindtrack.db).
- SessionLocal: sessionmaker configured for application use.
- get_db(): FastAPI dependency that yields a DB session.
- init_db(): create all tables from models that inherit from Base.

Environment:
- Set DATABASE_URL to switch databases, e.g.:
    postgres://user:pass@localhost:5432/dbname
  Default is SQLite file at ./mindtrack.db
"""



# Read DB URL from environment, default to sqlite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindtrack.db")

# If using SQLite, disable same-thread check (required for SQLite + multithreaded frameworks)
# For PostgreSQL, ensure SSL mode is properly set
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif DATABASE_URL.startswith("postgresql"):
    # Railway provides PostgreSQL URLs with SSL enabled
    connect_args["sslmode"] = "require"

# Create engine
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# Declarative base for models to inherit from
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it's closed.
    Usage in path operation:

        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Create all database tables for models that inherit from Base.
    Call this on application startup (e.g. in FastAPI startup event).
    """
    Base.metadata.create_all(bind=engine)


# Usage notes:
# - To define models, import Base:
#     from app.db.database import Base
#     class User(Base):
#         __tablename__ = "users"
#         ...
#
# - Call init_db() on application startup to ensure tables exist:
#     from fastapi import FastAPI
#     from app.db.database import init_db
#
#     app = FastAPI()
#
#     @app.on_event("startup")
#     def on_startup():
#         init_db()