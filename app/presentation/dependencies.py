from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services.auth_service import decode_token
from app.domain.exceptions import TokenInvalido
from app.infrastructure.database import get_db
from app.infrastructure.repositories import usuario_repository

bearer = HTTPBearer(auto_error=False)


def get_usuario_actual(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales requeridas.")
    try:
        payload = decode_token(credentials.credentials, "access")
        usuario = usuario_repository.obtener(int(payload["sub"]), db=db)
        if usuario is not None and int(payload.get("tv", usuario.token_version)) != usuario.token_version:
            usuario = None
    except (ValueError, TypeError, TokenInvalido):
        usuario = None
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado.")
    return usuario


def get_admin_actual(usuario=Depends(get_usuario_actual)):
    if usuario.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requieren permisos de administrador.")
    return usuario


def require_owner_or_admin(usuario_actual, propietario_id: int) -> None:
    if usuario_actual.role != "admin" and usuario_actual.id != propietario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para operar sobre este recurso.",
        )

__all__ = [
    "get_db",
    "get_usuario_actual",
    "get_admin_actual",
    "require_owner_or_admin",
]