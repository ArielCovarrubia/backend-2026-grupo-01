from app.domain.registro_habito import RegistroHabito
from app.infrastructure.models.registro_model import RegistroHabitoModel


def registro_a_dominio(model: RegistroHabitoModel) -> RegistroHabito:
    return RegistroHabito(
        id=model.id,
        habito_id=model.habito_id,
        fecha_registro=model.fecha_registro,
        completado=model.completado,
        valor_medido=model.valor_medido,
        nota=model.nota,
        creado_en=model.creado_en,
    )


def registro_a_modelo(entity: RegistroHabito) -> RegistroHabitoModel:
    return RegistroHabitoModel(
        id=entity.id if entity.id != 0 else None,
        habito_id=entity.habito_id,
        fecha_registro=entity.fecha_registro,
        completado=entity.completado,
        valor_medido=entity.valor_medido,
        nota=entity.nota,
        creado_en=entity.creado_en,
    )

