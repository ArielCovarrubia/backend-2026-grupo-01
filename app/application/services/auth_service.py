import hashlib
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.domain.usuario import Usuario
from app.infrastructure.models.password_reset_token_model import PasswordResetTokenModel
from app.infrastructure.models.refresh_token_model import RefreshTokenModel
from app.infrastructure.models.usuario_model import UsuarioModel

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7
RESET_TOKEN_MINUTES = 15
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-only-secret-change-in-production-32-bytes",
)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str | None) -> bool:
    return bool(hashed_password) and password_hash.verify(password, hashed_password)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(subject: int, token_type: str, expires_delta: timedelta, jti: str | None = None) -> str:
    now = _now()
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti or str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise jwt.InvalidTokenError("Tipo de token inválido.")
    return payload


def create_access_token(usuario_id: int) -> str:
    return _encode(usuario_id, "access", timedelta(minutes=ACCESS_TOKEN_MINUTES))


def create_refresh_token(usuario_id: int, db: Session) -> str:
    jti = str(uuid.uuid4())
    token = _encode(usuario_id, "refresh", timedelta(days=REFRESH_TOKEN_DAYS), jti)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    db.add(
        RefreshTokenModel(
            jti=jti,
            usuario_id=usuario_id,
            token_hash=_token_hash(token),
            expira_en=datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None),
        )
    )
    db.commit()
    return token


def rotate_refresh_token(token: str, db: Session) -> tuple[str, str] | None:
    try:
        payload = decode_token(token, "refresh")
    except jwt.InvalidTokenError:
        return None
    registro = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.jti == payload["jti"], RefreshTokenModel.revocado_en.is_(None))
        .first()
    )
    if registro is None or registro.token_hash != _token_hash(token):
        return None
    registro.revocado_en = _now().replace(tzinfo=None)
    nuevo = create_refresh_token(int(payload["sub"]), db)
    return nuevo, payload["sub"]


def revoke_refresh_token(token: str, db: Session) -> bool:
    try:
        payload = decode_token(token, "refresh")
    except jwt.InvalidTokenError:
        return False
    registro = db.query(RefreshTokenModel).filter(
        RefreshTokenModel.jti == payload["jti"],
        RefreshTokenModel.revocado_en.is_(None),
    ).first()
    if registro is None or registro.token_hash != _token_hash(token):
        return False
    registro.revocado_en = _now().replace(tzinfo=None)
    db.commit()
    return True


def revoke_all_sessions(usuario_id: int, db: Session) -> None:
    db.query(RefreshTokenModel).filter(
        RefreshTokenModel.usuario_id == usuario_id,
        RefreshTokenModel.revocado_en.is_(None),
    ).update({"revocado_en": _now().replace(tzinfo=None)})
    db.commit()


def create_reset_token(usuario: Usuario, db: Session) -> str:
    jti = str(uuid.uuid4())
    token = _encode(usuario.id, "reset", timedelta(minutes=RESET_TOKEN_MINUTES), jti)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    db.add(
        PasswordResetTokenModel(
            jti=jti,
            usuario_id=usuario.id,
            expira_en=datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None),
        )
    )
    db.commit()
    return token


def reset_password(token: str, new_password: str, db: Session) -> bool:
    try:
        payload = decode_token(token, "reset")
    except jwt.InvalidTokenError:
        return False
    registro = (
        db.query(PasswordResetTokenModel)
        .filter(
            PasswordResetTokenModel.jti == payload["jti"],
            PasswordResetTokenModel.usado_en.is_(None),
        )
        .first()
    )
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == int(payload["sub"])).first()
    if registro is None or usuario is None:
        return False
    usuario.password_hash = hash_password(new_password)
    registro.usado_en = _now().replace(tzinfo=None)
    db.commit()
    revoke_all_sessions(usuario.id, db)
    return True


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
