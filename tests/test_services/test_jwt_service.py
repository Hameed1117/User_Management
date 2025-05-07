import pytest
from app.services import jwt_service


def test_create_access_token_upcases_role_and_decodes():
    """
    • Ensures create_access_token converts `role` to uppercase
    • Round‑trip through decode_token covers both functions
    """
    token   = jwt_service.create_access_token(
        data={"sub": "42", "role": "admin"}
    )
    payload = jwt_service.decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"          # upper‑cased


def test_decode_token_invalid_returns_none():
    """Passing a clearly malformed JWT should return None."""
    assert jwt_service.decode_token("not.a.jwt") is None
