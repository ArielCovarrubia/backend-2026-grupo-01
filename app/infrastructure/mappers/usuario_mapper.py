from app.domain.usuario import Usuario
from app.infrastructure.models.usuario_model import UsuarioModel


def usuario_a_dominio(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        name=model.name,
        email=model.email,
        fecha_registro=model.fecha_registro,
        zona_horaria=model.zona_horaria,
        password_hash=model.password_hash,
        role=model.role,
        intentos_fallidos=model.intentos_fallidos,
        bloqueado_hasta=model.bloqueado_hasta,
        token_version=model.token_version,
    )


def usuario_a_modelo(entity: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entity.id if entity.id != 0 else None,
        name=entity.name,
        email=str(entity.email),
        fecha_registro=entity.fecha_registro,
        zona_horaria=entity.zona_horaria,
        password_hash=entity.password_hash,
        role=entity.role,
        intentos_fallidos=entity.intentos_fallidos,
        bloqueado_hasta=entity.bloqueado_hasta,
        token_version=entity.token_version,
    )