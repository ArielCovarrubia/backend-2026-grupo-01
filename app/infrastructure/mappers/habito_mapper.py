from app.domain.habito import EstadoHabito, Habito
from app.infrastructure.models.habito_model import HabitoModel


def habito_a_dominio(model: HabitoModel) -> Habito:
    return Habito(
        id=model.id,
        usuario_id=model.usuario_id,
        categoria_id=model.categoria_id,
        nombre=model.nombre,
        frecuencia_semanal=model.frecuencia_semanal,
        estado=EstadoHabito(model.estado) if isinstance(model.estado, str) else model.estado,
        fecha_creacion=model.fecha_creacion,
    )


def habito_a_modelo(entity: Habito) -> HabitoModel:
    return HabitoModel(
        id=entity.id if entity.id != 0 else None,
        usuario_id=entity.usuario_id,
        categoria_id=entity.categoria_id,
        nombre=entity.nombre,
        frecuencia_semanal=entity.frecuencia_semanal,
        estado=entity.estado.value if hasattr(entity.estado, "value") else str(entity.estado),
        fecha_creacion=entity.fecha_creacion,
    )

