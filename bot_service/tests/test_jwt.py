from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def test_decode_and_validate_ok():
    payload = {
        "sub": "42",
        "role": "user",
        "exp": int((datetime.now(tz=UTC) + timedelta(minutes=10)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

    decoded = decode_and_validate(token)
    assert decoded["sub"] == "42"


def test_decode_and_validate_invalid_token_raises():
    with pytest.raises(ValueError):
        decode_and_validate("not-a-jwt")
