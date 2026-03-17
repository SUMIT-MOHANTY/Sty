from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator

from app.core.config import settings

# Create SQLAlchemy engine with proper connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Verify connections before use to prevent stale connections
    pool_size=10,        # Maximum number of connections to keep in the pool
    max_overflow=20,     # Maximum number of connections to create above pool_size
    pool_recycle=3600    # Recycle connections every hour to handle database timeouts
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator:
    """
    Database session dependency

    Yields:
        Session: SQLAlchemy session

    Raises:
        Exception: Any exception that occurs during the session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions outside of request context

    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
