from app.domain.usuario import Usuario

_usuarios: dict[int, Usuario] = {}
_contador_id = 0


def guardar(usuario: Usuario) -> Usuario:
    global _contador_id
    _contador_id += 1
    usuario.id = _contador_id
    _usuarios[usuario.id] = usuario
    return usuario


def listar() -> list[Usuario]:
    return list(_usuarios.values())


def obtener(usuario_id: int) -> Usuario | None:
    return _usuarios.get(usuario_id)


def actualizar(usuario_id: int, usuario: Usuario) -> Usuario | None:
    if usuario_id not in _usuarios:
        return None
    usuario.id = usuario_id
    _usuarios[usuario_id] = usuario
    return usuario


def eliminar(usuario_id: int) -> bool:
    return _usuarios.pop(usuario_id, None) is not None


def existe(usuario_id: int) -> bool:
    return usuario_id in _usuarios


def obtener_por_email(email: str) -> Usuario | None:
    email_normalizado = str(email).casefold()
    for usuario in _usuarios.values():
        if str(usuario.email).casefold() == email_normalizado:
            return usuario
    return None

