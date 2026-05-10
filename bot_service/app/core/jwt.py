from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except ExpiredSignatureError as exc:
        raise ValueError("Token expired") from exc
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    if "sub" not in payload:
        raise ValueError("Missing sub in token")
    return payload
