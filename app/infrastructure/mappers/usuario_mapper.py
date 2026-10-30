from app.domain.usuario import Usuario
from app.infrastructure.models.usuario_model import UsuarioModel


def usuario_a_dominio(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        name=model.name,
        email=model.email,
        fecha_registro=model.fecha_registro,
    )


def usuario_a_modelo(entity: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entity.id if entity.id != 0 else None,
        name=entity.name,
        email=str(entity.email),
        fecha_registro=entity.fecha_registro,
    )

