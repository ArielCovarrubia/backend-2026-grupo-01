from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.categoria import Categoria
from app.infrastructure.database import SessionLocal
from app.infrastructure.mappers.categoria_mapper import categoria_a_dominio, categoria_a_modelo
from app.infrastructure.models.categoria_model import CategoriaModel

_categorias: dict[int, Categoria] = {}
_contador_id = 0


def _get_session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def guardar(categoria: Categoria, db: Session | None = None) -> Categoria:
    s, close = _get_session(db)
    try:
        modelo = categoria_a_modelo(categoria)
        s.add(modelo)
        s.commit()
        s.refresh(modelo)
        return categoria_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def listar(db: Session | None = None) -> list[Categoria]:
    s, close = _get_session(db)
    try:
        modelos = s.query(CategoriaModel).order_by(CategoriaModel.id.asc()).all()
        return [categoria_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def listar_activas(db: Session | None = None) -> list[Categoria]:
    s, close = _get_session(db)
    try:
        modelos = (
            s.query(CategoriaModel)
            .filter(CategoriaModel.activa.is_(True))
            .order_by(CategoriaModel.id.asc())
            .all()
        )
        return [categoria_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def obtener(categoria_id: int, db: Session | None = None) -> Categoria | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
        return categoria_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()


def obtener_por_nombre(nombre: str, db: Session | None = None) -> Categoria | None:
    s, close = _get_session(db)
    try:
        nombre_norm = str(nombre).casefold()
        modelo = s.query(CategoriaModel).filter(func.lower(CategoriaModel.nombre) == nombre_norm).first()
        return categoria_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()


def existe(categoria_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return s.query(CategoriaModel.id).filter(CategoriaModel.id == categoria_id).first() is not None
    finally:
        if close:
            s.close()


def actualizar(categoria_id: int, categoria: Categoria, db: Session | None = None) -> Categoria | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
        if not modelo:
            return None
        modelo.nombre = categoria.nombre
        modelo.descripcion = categoria.descripcion
        modelo.activa = categoria.activa
        if hasattr(categoria, "orden_prioridad"):
            modelo.orden_prioridad = categoria.orden_prioridad
        s.commit()
        s.refresh(modelo)
        return categoria_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def eliminar(categoria_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        modelo = s.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
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
