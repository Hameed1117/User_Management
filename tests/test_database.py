import pytest
from app.database import Database
from sqlalchemy.ext.asyncio import AsyncSession

def test_initialize_skips_if_already_initialized(monkeypatch):
    """Ensure initialize does not overwrite existing engine/session."""
    Database._engine = "dummy_engine"
    Database._session_factory = "dummy_factory"

    # Try initializing again — should skip
    Database.initialize("postgresql+asyncpg://user:password@postgres/myappdb")

    assert Database._engine == "dummy_engine"
    assert Database._session_factory == "dummy_factory"

@pytest.mark.asyncio
async def test_initialize_actually_creates_engine_and_session():
    """Ensure real initialization sets engine and session factory."""
    # Clear state
    Database._engine = None
    Database._session_factory = None

    Database.initialize("postgresql+asyncpg://user:password@postgres/myappdb")

    session_factory = Database.get_session_factory()
    session = session_factory()
    assert isinstance(session, AsyncSession)

def test_get_session_factory_without_initialize_raises():
    """Should raise ValueError if get_session_factory is called before init."""
    # Reset state
    Database._session_factory = None
    Database._engine = None

    with pytest.raises(ValueError, match="Database not initialized"):
        Database.get_session_factory()
