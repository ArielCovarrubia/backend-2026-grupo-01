from app.domain.habito import Habito

_habitos: dict[int, Habito] = {}
_contador_id = 0


def guardar(habito: Habito) -> Habito:
    global _contador_id
    _contador_id += 1
    habito.id = _contador_id
    _habitos[habito.id] = habito
    return habito


def listar() -> list[Habito]:
    return list(_habitos.values())


def obtener(habito_id: int) -> Habito | None:
    return _habitos.get(habito_id)


def listar_por_usuario(usuario_id: int) -> list[Habito]:
    return [h for h in _habitos.values() if h.usuario_id == usuario_id]


def listar_por_categoria(categoria_id: int) -> list[Habito]:
    return [h for h in _habitos.values() if h.categoria_id == categoria_id]


def existe_por_categoria(categoria_id: int) -> bool:
    return any(h.categoria_id == categoria_id for h in _habitos.values())


def actualizar(habito_id: int, habito: Habito) -> Habito | None:
    if habito_id not in _habitos:
        return None
    habito.id = habito_id
    _habitos[habito_id] = habito
    return habito


def eliminar(habito_id: int) -> bool:
    return _habitos.pop(habito_id, None) is not None


def existe(habito_id: int) -> bool:
    return habito_id in _habitos
