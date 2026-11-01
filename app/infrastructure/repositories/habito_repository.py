import math
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.habito import Habito
from app.infrastructure.database import SessionLocal
from app.infrastructure.mappers.habito_mapper import habito_a_dominio, habito_a_modelo
from app.infrastructure.models.habito_model import HabitoModel

_habitos: dict[int, Habito] = {}
_contador_id = 0


def _get_session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def guardar(habito: Habito, db: Session | None = None) -> Habito:
    s, close = _get_session(db)
    try:
        modelo = habito_a_modelo(habito)
        s.add(modelo)
        s.commit()
        s.refresh(modelo)
        return habito_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def listar(db: Session | None = None) -> list[Habito]:
    s, close = _get_session(db)
    try:
        modelos = s.query(HabitoModel).order_by(HabitoModel.id.asc()).all()
        return [habito_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def obtener(habito_id: int, db: Session | None = None) -> Habito | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(HabitoModel).filter(HabitoModel.id == habito_id).first()
        return habito_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()


def listar_por_usuario(usuario_id: int, db: Session | None = None) -> list[Habito]:
    s, close = _get_session(db)
    try:
        modelos = (
            s.query(HabitoModel)
            .filter(HabitoModel.usuario_id == usuario_id)
            .order_by(HabitoModel.id.asc())
            .all()
        )
        return [habito_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def listar_por_categoria(categoria_id: int, db: Session | None = None) -> list[Habito]:
    s, close = _get_session(db)
    try:
        modelos = (
            s.query(HabitoModel)
            .filter(HabitoModel.categoria_id == categoria_id)
            .order_by(HabitoModel.id.asc())
            .all()
        )
        return [habito_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def existe_por_categoria(categoria_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return s.query(HabitoModel.id).filter(HabitoModel.categoria_id == categoria_id).first() is not None
    finally:
        if close:
            s.close()


def actualizar(habito_id: int, habito: Habito, db: Session | None = None) -> Habito | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(HabitoModel).filter(HabitoModel.id == habito_id).first()
        if not modelo:
            return None
        modelo.nombre = habito.nombre
        modelo.frecuencia_semanal = habito.frecuencia_semanal
        modelo.categoria_id = habito.categoria_id
        modelo.estado = habito.estado.value if hasattr(habito.estado, "value") else str(habito.estado)
        s.commit()
        s.refresh(modelo)
        return habito_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def eliminar(habito_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        modelo = s.query(HabitoModel).filter(HabitoModel.id == habito_id).first()
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


def existe(habito_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return s.query(HabitoModel.id).filter(HabitoModel.id == habito_id).first() is not None
    finally:
        if close:
            s.close()


def buscar_paginado(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    estado: str | None = None,
    ordenar_por: str = "nombre",
    direccion: str = "asc",
    pagina: int = 1,
    limite: int = 10,
    db: Session | None = None,
) -> tuple[list[Habito], int, int]:
    s, close = _get_session(db)
    try:
        query = s.query(HabitoModel)

        if usuario_id is not None:
            query = query.filter(HabitoModel.usuario_id == usuario_id)

        if categoria_id is not None:
            query = query.filter(HabitoModel.categoria_id == categoria_id)

        if estado is not None:
            query = query.filter(func.upper(HabitoModel.estado) == estado.upper())

        columnas_orden = {
            "nombre": HabitoModel.nombre,
            "frecuencia_semanal": HabitoModel.frecuencia_semanal,
            "fecha_creacion": HabitoModel.fecha_creacion,
        }
        col = columnas_orden.get(ordenar_por, HabitoModel.nombre)
        col_ordenada = col.desc() if direccion.lower() == "desc" else col.asc()
        query = query.order_by(col_ordenada, HabitoModel.id.asc())

        total = query.count()
        total_paginas = math.ceil(total / limite) if total > 0 else 1

        offset = (pagina - 1) * limite
        modelos = query.offset(offset).limit(limite).all()
        return [habito_a_dominio(m) for m in modelos], total, total_paginas
    finally:
        if close:
            s.close()
