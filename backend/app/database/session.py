"""
AI Chargeback Guardian — Database Session Management
Provides SQLAlchemy engine, session factory, and FastAPI dependency.
Configured for robust SQLite concurrency and memory journaling.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# SQLite requires check_same_thread=False for multi-threaded access
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

# Apply SQLite pragmas for robust Windows/OneDrive disk I/O reliability
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = MEMORY")
        cursor.execute("PRAGMA synchronous = OFF")
        cursor.execute("PRAGMA temp_store = MEMORY")
        cursor.execute("PRAGMA busy_timeout = 30000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
