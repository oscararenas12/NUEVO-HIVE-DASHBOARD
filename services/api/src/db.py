"""Database engine and session dependency.

The engine is built from the active database URL (real DB in normal runs; the
test DB when TESTING is set -- see config.py). Endpoints depend on get_session,
which the test suite overrides with a rollback-scoped session.
See https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from src.config import get_settings

engine = create_engine(get_settings().active_database_url)


def get_session() -> Iterator[Session]:
    """Yield a database session for the lifetime of one request."""
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """Create all tables from the SQLModel metadata (used by tests/bootstrap).

    At runtime, Alembic migrations own schema creation (Phase 2 Branch B).
    """
    SQLModel.metadata.create_all(engine)
