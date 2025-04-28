import pytest
from app.utils import common
import logging.config

def test_setup_logging(monkeypatch):
    """
    Test setup_logging safely by mocking fileConfig to avoid file not found error.
    """
    # Mock fileConfig to do nothing
    monkeypatch.setattr(logging.config, "fileConfig", lambda *args, **kwargs: None)

    try:
        common.setup_logging()
    except Exception as e:
        pytest.fail(f"setup_logging() raised an exception: {e}")
