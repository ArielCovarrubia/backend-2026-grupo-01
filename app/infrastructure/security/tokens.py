import hashlib
import os
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.domain.exceptions import TokenInvalido

ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY no está configurada.")


def encode_token(
    subject: int,
    token_type: str,
    expires_delta: timedelta,
    jti: str | None = None,
    token_version: int | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti or str(uuid.uuid4()),
    }
    if token_version is not None:
        payload["tv"] = token_version
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    """Valida firma, vigencia y propósito. Lanza TokenInvalido si algo falla."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise TokenInvalido() from exc
    if (
        payload.get("type") != expected_type
        or not payload.get("sub")
        or not payload.get("jti")
        or "exp" not in payload
    ):
        raise TokenInvalido("Tipo de token inválido.")
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()