import pytest
from datetime import timedelta
from app.services import jwt_service


def test_create_access_token_role_branch_and_decode():
    token = jwt_service.create_access_token(
        data={"sub": "u1", "role": "member"},
        expires_delta=timedelta(seconds=1),
    )
    decoded = jwt_service.decode_token(token)
    assert decoded["role"] == "MEMBER"    # branch lines 21‑22 now covered


def test_decode_token_exception_branch():
    assert jwt_service.decode_token("bad.jwt.token") is None
