from datetime import date
from sqlalchemy.orm import Session

from app.domain.registro_habito import RegistroHabito
from app.infrastructure.database import SessionLocal
from app.infrastructure.mappers.registro_mapper import registro_a_dominio, registro_a_modelo
from app.infrastructure.models.registro_model import RegistroHabitoModel

_registros: dict[int, RegistroHabito] = {}
_contador_id = 0


def _get_session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def guardar(registro: RegistroHabito, db: Session | None = None) -> RegistroHabito:
    s, close = _get_session(db)
    try:
        modelo = registro_a_modelo(registro)
        s.add(modelo)
        s.commit()
        s.refresh(modelo)
        return registro_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def listar(db: Session | None = None) -> list[RegistroHabito]:
    s, close = _get_session(db)
    try:
        modelos = s.query(RegistroHabitoModel).order_by(RegistroHabitoModel.id.asc()).all()
        return [registro_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def obtener(registro_id: int, db: Session | None = None) -> RegistroHabito | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(RegistroHabitoModel).filter(RegistroHabitoModel.id == registro_id).first()
        return registro_a_dominio(modelo) if modelo else None
    finally:
        if close:
            s.close()


def listar_por_habito(habito_id: int, db: Session | None = None) -> list[RegistroHabito]:
    s, close = _get_session(db)
    try:
        modelos = (
            s.query(RegistroHabitoModel)
            .filter(RegistroHabitoModel.habito_id == habito_id)
            .order_by(RegistroHabitoModel.fecha_registro.asc(), RegistroHabitoModel.id.asc())
            .all()
        )
        return [registro_a_dominio(m) for m in modelos]
    finally:
        if close:
            s.close()


def existe_registro_en_fecha(habito_id: int, fecha: date, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return (
            s.query(RegistroHabitoModel.id)
            .filter(
                RegistroHabitoModel.habito_id == habito_id,
                RegistroHabitoModel.fecha_registro == fecha,
            )
            .first()
            is not None
        )
    finally:
        if close:
            s.close()


def actualizar(registro_id: int, registro: RegistroHabito, db: Session | None = None) -> RegistroHabito | None:
    s, close = _get_session(db)
    try:
        modelo = s.query(RegistroHabitoModel).filter(RegistroHabitoModel.id == registro_id).first()
        if not modelo:
            return None
        modelo.completado = registro.completado
        modelo.valor_medido = registro.valor_medido
        modelo.nota = registro.nota
        s.commit()
        s.refresh(modelo)
        return registro_a_dominio(modelo)
    except Exception:
        s.rollback()
        raise
    finally:
        if close:
            s.close()


def eliminar(registro_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        modelo = s.query(RegistroHabitoModel).filter(RegistroHabitoModel.id == registro_id).first()
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


def existe(registro_id: int, db: Session | None = None) -> bool:
    s, close = _get_session(db)
    try:
        return s.query(RegistroHabitoModel.id).filter(RegistroHabitoModel.id == registro_id).first() is not None
    finally:
        if close:
            s.close()
