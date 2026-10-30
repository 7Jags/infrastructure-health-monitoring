
"""Database configuration for PostgreSQL."""

from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=settings.database_port,
    database=settings.database_name,
    query={"sslmode": settings.database_sslmode},
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def initialise_database() -> None:
    """Create missing tables when explicitly requested."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session and close it after use."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()