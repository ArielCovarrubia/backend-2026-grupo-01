from app.domain.categoria import Categoria

_categorias: dict[int, Categoria] = {}
_contador_id = 0


def guardar(categoria: Categoria) -> Categoria:
    global _contador_id
    _contador_id += 1
    categoria.id = _contador_id
    _categorias[categoria.id] = categoria
    return categoria


def listar() -> list[Categoria]:
    return list(_categorias.values())


def listar_activas() -> list[Categoria]:
    return [c for c in _categorias.values() if c.activa]


def obtener(categoria_id: int) -> Categoria | None:
    return _categorias.get(categoria_id)


def existe(categoria_id: int) -> bool:
    return categoria_id in _categorias


def actualizar(categoria_id: int, categoria: Categoria) -> Categoria | None:
    if categoria_id not in _categorias:
        return None
    categoria.id = categoria_id
    _categorias[categoria_id] = categoria
    return categoria


def eliminar(categoria_id: int) -> bool:
    return _categorias.pop(categoria_id, None) is not None
