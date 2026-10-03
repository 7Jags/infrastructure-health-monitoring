
"""Shared PostgreSQL fixtures for integration tests."""

import pytest
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base
from app import models  # noqa: F401 - register all models with Base.metadata


@pytest.fixture(scope="session")
def test_engine():
    """Connect only to the dedicated Project1_test database."""

    test_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.database_username,
        password=settings.database_password,
        host=settings.database_hostname,
        port=settings.database_port,
        database="Project1_test",
    )

    # Safety check: never run integration tests against the real database.
    if test_url.database != "Project1_test":
        raise RuntimeError("Tests must use the Project1_test database.")

    engine = create_engine(test_url, pool_pre_ping=True)

    # Create missing tables without deleting existing tables or records.
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Give each test a transaction that is rolled back afterward."""

    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()