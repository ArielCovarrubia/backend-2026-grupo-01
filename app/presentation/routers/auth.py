from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.application.services import auth_service
from app.infrastructure.repositories import usuario_repository
from app.presentation.dependencies import get_db
from app.presentation.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=auth_service.REFRESH_TOKEN_DAYS * 86400,
        path="/auth",
    )


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, response: Response, db: Session = Depends(get_db)):
    usuario = usuario_repository.obtener_por_email(str(datos.email), db=db)
    if usuario is None or not auth_service.verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos.")
    refresh = auth_service.create_refresh_token(usuario.id, db)
    _set_refresh_cookie(response, refresh)
    return {"access_token": auth_service.create_access_token(usuario.id), "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    token = refresh_token
    if token is None:
        raise HTTPException(status_code=401, detail="Refresh token requerido.")
    rotated = auth_service.rotate_refresh_token(token, db)
    if rotated is None:
        raise HTTPException(status_code=401, detail="Refresh token inválido o revocado.")
    nuevo_refresh, usuario_id = rotated
    _set_refresh_cookie(response, nuevo_refresh)
    return {"access_token": auth_service.create_access_token(int(usuario_id)), "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        auth_service.revoke_refresh_token(refresh_token, db)
    response.delete_cookie("refresh_token", path="/auth")


@router.post("/forgot-password")
def forgot_password(datos: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario = usuario_repository.obtener_por_email(str(datos.email), db=db)
    if usuario is None:
        return {"message": "Si el correo existe, se enviará un enlace de recuperación."}
    token = auth_service.create_reset_token(usuario, db)
    return {"message": "Si el correo existe, se enviará un enlace de recuperación.", "token": token}


@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not auth_service.reset_password(datos.token, datos.password, db):
        raise HTTPException(status_code=400, detail="Token de recuperación inválido, usado o expirado.")
    return {"message": "Contraseña actualizada correctamente."}
