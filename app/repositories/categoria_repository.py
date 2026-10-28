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