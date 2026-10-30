from app.domain.exceptions import ConflictoError, RecursoNoEncontradoError
from app.domain.usuario import Usuario
from app.infrastructure.repositories import habito_repository, usuario_repository
from app.presentation.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate


def crear_usuario(datos: UsuarioCreate) -> Usuario:
    usuario_existente = usuario_repository.obtener_por_email(str(datos.email))
    if usuario_existente is not None:
        raise ConflictoError("El usuario con este correo electrónico ya existe.")

    usuario = Usuario(
        id=0,
        name=datos.name,
        email=str(datos.email),
    )
    return usuario_repository.guardar(usuario)


def listar_usuarios() -> list[Usuario]:
    return usuario_repository.listar()


def obtener_usuario(usuario_id: int) -> Usuario:
    usuario = usuario_repository.obtener(usuario_id)
    if usuario is None:
        raise RecursoNoEncontradoError(f"No existe un usuario con el ID {usuario_id}.")
    return usuario


def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate) -> Usuario:
    usuario_actual = usuario_repository.obtener(usuario_id)
    if usuario_actual is None:
        raise RecursoNoEncontradoError(f"No existe un usuario con el ID {usuario_id}.")

    if datos.name is not None:
        usuario_actual.name = datos.name

    if datos.email is not None:
        usuario_con_email = usuario_repository.obtener_por_email(str(datos.email))
        if usuario_con_email is not None and usuario_con_email.id != usuario_id:
            raise ConflictoError("El correo electrónico ya está en uso por otro usuario.")
        usuario_actual.email = str(datos.email)

    return usuario_repository.actualizar(usuario_id, usuario_actual)


def eliminar_usuario(usuario_id: int) -> None:
    usuario_existente = usuario_repository.obtener(usuario_id)
    if usuario_existente is None:
        raise RecursoNoEncontradoError(f"No existe un usuario con el ID {usuario_id}.")

    habitos_usuario = habito_repository.listar_por_usuario(usuario_id)
    if habitos_usuario:
        raise ConflictoError("No se puede eliminar el usuario porque tiene hábitos asociados.")

    usuario_repository.eliminar(usuario_id)

