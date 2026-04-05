from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    raw_password = "super-secret-password"
    password_hash = hash_password(raw_password)

    assert password_hash != raw_password
    assert verify_password(raw_password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_create_and_decode_token():
    token = create_access_token(sub="123", role="user", expires_minutes=10)
    payload = decode_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload
