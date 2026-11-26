import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.domain.exceptions import TokenInvalido
from app.domain.usuario import Usuario
from app.infrastructure.models.password_reset_token_model import PasswordResetTokenModel
from app.infrastructure.models.refresh_token_model import RefreshTokenModel
from app.infrastructure.models.usuario_model import UsuarioModel
from app.infrastructure.security.passwords import hash_password, verify_password
from app.infrastructure.security.tokens import decode_token, encode_token, hash_token

ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7
RESET_TOKEN_MINUTES = 15

__all__ = [
    "ACCESS_TOKEN_MINUTES",
    "REFRESH_TOKEN_DAYS",
    "RESET_TOKEN_MINUTES",
    "create_access_token",
    "create_refresh_token",
    "create_reset_token",
    "decode_token",
    "hash_password",
    "reset_password",
    "revoke_all_sessions",
    "revoke_refresh_token",
    "rotate_refresh_token",
    "verify_password",
]


def _now() -> datetime:
    return datetime.now(UTC)


def _expiration(token: str, token_type: str) -> datetime:
    """Vencimiento de un token propio, en UTC sin zona para la base de datos."""
    exp = decode_token(token, token_type)["exp"]
    return datetime.fromtimestamp(exp, tz=UTC).replace(tzinfo=None)


def create_access_token(usuario_id: int) -> str:
    return encode_token(usuario_id, "access", timedelta(minutes=ACCESS_TOKEN_MINUTES))


def create_refresh_token(usuario_id: int, db: Session) -> str:
    jti = str(uuid.uuid4())
    token = encode_token(usuario_id, "refresh", timedelta(days=REFRESH_TOKEN_DAYS), jti)
    db.add(
        RefreshTokenModel(
            jti=jti,
            usuario_id=usuario_id,
            token_hash=hash_token(token),
            expira_en=_expiration(token, "refresh"),
        )
    )
    db.commit()
    return token


def rotate_refresh_token(token: str, db: Session) -> tuple[str, str] | None:
    try:
        payload = decode_token(token, "refresh")
    except TokenInvalido:
        return None
    registro = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.jti == payload["jti"], RefreshTokenModel.revocado_en.is_(None))
        .first()
    )
    if registro is None or registro.token_hash != hash_token(token):
        return None
    registro.revocado_en = _now().replace(tzinfo=None)
    nuevo = create_refresh_token(int(payload["sub"]), db)
    return nuevo, payload["sub"]


def revoke_refresh_token(token: str, db: Session) -> bool:
    try:
        payload = decode_token(token, "refresh")
    except TokenInvalido:
        return False
    registro = db.query(RefreshTokenModel).filter(
        RefreshTokenModel.jti == payload["jti"],
        RefreshTokenModel.revocado_en.is_(None),
    ).first()
    if registro is None or registro.token_hash != hash_token(token):
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
    token = encode_token(usuario.id, "reset", timedelta(minutes=RESET_TOKEN_MINUTES), jti)
    db.add(
        PasswordResetTokenModel(
            jti=jti,
            usuario_id=usuario.id,
            expira_en=_expiration(token, "reset"),
        )
    )
    db.commit()
    return token


def reset_password(token: str, new_password: str, db: Session) -> bool:
    try:
        payload = decode_token(token, "reset")
    except TokenInvalido:
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