import logging
import smtplib
from datetime import timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.application.services import auth_service
from app.infrastructure.models.password_reset_token_model import PasswordResetTokenModel
from app.infrastructure.repositories import usuario_repository
from app.infrastructure.security.email import send_password_reset_email
from app.presentation.dependencies import get_db
from app.presentation.dependencies import get_usuario_actual
from app.presentation.schemas.auth_schema import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.presentation.security.cookies import clear_refresh_cookie, set_refresh_cookie

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, response: Response, db: Session = Depends(get_db)):
    usuario = usuario_repository.obtener_por_email(str(datos.email), db=db)
    if usuario is not None and usuario.esta_bloqueado():
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos.")
    if usuario is None or not usuario.password_hash or not auth_service.verify_password(datos.password, usuario.password_hash):
        if usuario is not None:
            usuario.registrar_fallo()
            usuario_repository.actualizar(usuario.id, usuario, db=db)
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos.")
    usuario.reiniciar_intentos()
    usuario_repository.actualizar(usuario.id, usuario, db=db)
    refresh = auth_service.create_refresh_token(usuario.id, db, token_version=usuario.token_version)
    set_refresh_cookie(response, refresh)
    return {
        "access_token": auth_service.create_access_token(usuario.id, usuario.token_version),
        "token_type": "bearer",
    }


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
    set_refresh_cookie(response, nuevo_refresh)
    usuario = usuario_repository.obtener(int(usuario_id), db=db)
    return {
        "access_token": auth_service.create_access_token(
            int(usuario_id),
            usuario.token_version if usuario else 0,
        ),
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if refresh_token:
        auth_service.revoke_refresh_token(refresh_token, db)
    clear_refresh_cookie(response)


@router.post("/forgot-password")
def forgot_password(datos: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario = usuario_repository.obtener_por_email(str(datos.email), db=db)
    if usuario is not None:
        recientes = (
            db.query(PasswordResetTokenModel)
            .filter(
                PasswordResetTokenModel.usuario_id == usuario.id,
                PasswordResetTokenModel.expira_en
                >= auth_service._now().replace(tzinfo=None) - timedelta(minutes=15),
            )
            .count()
        )
        if recientes < 5:
            token = auth_service.create_reset_token(usuario, db)
            try:
                send_password_reset_email(str(datos.email), token)
            except (OSError, smtplib.SMTPException):
                logging.getLogger(__name__).exception("No se pudo enviar el correo de recuperación.")
    return {"message": "Si el correo existe, se enviará un enlace de recuperación."}


@router.get("/me")
def obtener_usuario_actual(usuario_actual=Depends(get_usuario_actual)):
    return usuario_actual


@router.post("/reset-password")
def reset_password(datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not auth_service.reset_password(datos.token, datos.password, db):
        raise HTTPException(status_code=400, detail="Token de recuperación inválido, usado o expirado.")
    return {"message": "Contraseña actualizada correctamente."}