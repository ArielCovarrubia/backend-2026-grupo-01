from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.usuario import Usuario
from app.infrastructure.database import SessionLocal
from app.infrastructure.mappers.usuario_mapper import usuario_a_dominio, usuario_a_modelo
from app.infrastructure.models.usuario_model import UsuarioModel

_usuarios: dict[int, Usuario] = {}
_contador_id = 0


def _get_session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def guardar(usuario: Usuario, db: Session | None = None) -> Usuario:
    s, close = _get_session(db)
    try:
        modelo = usuario_a_modelo(usuario)
        s.add(modelo)
        s.commit()
        s.refresh(modelo)
        return usuario_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def listar(db: Session | None = None) -> list[Usuario]:
    s, close = _get_session(db)
    try:
        modelos = s.query(UsuarioModel).order_by(UsuarioModel.id.asc()).all()
        return [usuario_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def obtener(usuario_id: int, db: Session | None = None) -> Usuario | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return usuario_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()


def actualizar(usuario_id: int, usuario: Usuario, db: Session | None = None) -> Usuario | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if not modelo:
            return None
        modelo.name = usuario.name
        modelo.email = str(usuario.email)
        if hasattr(usuario, "zona_horaria") and usuario.zona_horaria:
            modelo.zona_horaria = usuario.zona_horaria
        s.commit()
        s.refresh(modelo)
        return usuario_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def eliminar(usuario_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        modelo = s.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if not modelo:
            return False
        s.delete(modelo)
        s.commit()
        return True
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def existe(usuario_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return s.query(UsuarioModel.id).filter(UsuarioModel.id == usuario_id).first() is not None
    finally:
        if close:
            s.close()


def obtener_por_email(email: str, db: Session | None = None) -> Usuario | None:
    s, close = _get_session(db)
    try:
        email_normalizado = str(email).casefold()
        modelo = s.query(UsuarioModel).filter(func.lower(UsuarioModel.email) == email_normalizado).first()
        return usuario_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()
