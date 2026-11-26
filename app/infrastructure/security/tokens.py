import hashlib
import os
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.domain.exceptions import TokenInvalido

ALGORITHM = "HS256"
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-only-secret-change-in-production-32-bytes",
)


def encode_token(
    subject: int, token_type: str, expires_delta: timedelta, jti: str | None = None
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti or str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    """Valida firma, vigencia y propósito. Lanza TokenInvalido si algo falla."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise TokenInvalido() from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise TokenInvalido("Tipo de token inválido.")
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()