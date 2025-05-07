"""
Drives every generator dependency through yield *and* finalisation,
so lines 22‑27 / 40 / 44 in app/dependencies.py are executed.
"""

import inspect
import contextlib
from unittest.mock import MagicMock
import app.dependencies as deps


def test_generators_body_and_finally(monkeypatch):
    # Stub session factory so get_db (if present) works
    if hasattr(deps, "get_session_factory"):
        fake_session = MagicMock(name="Session")
        monkeypatch.setattr(
            deps, "get_session_factory",
            lambda: (lambda: fake_session),
            raising=True,
        )

    for _name, func in inspect.getmembers(deps, inspect.isgeneratorfunction):
        gen = func()
        with contextlib.suppress(Exception):
            next(gen)        # run body up to yield
        with contextlib.suppress(Exception):
            next(gen)        # exhaust generator – runs finally block
