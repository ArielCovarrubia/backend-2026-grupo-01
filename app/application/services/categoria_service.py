from sqlalchemy.orm import Session

from app.domain.categoria import Categoria
from app.domain.exceptions import ConflictoError, RecursoNoEncontradoError, ReglaNegocioError
from app.infrastructure.repositories import categoria_repository, habito_repository
from app.presentation.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate


def listar_categorias(db: Session | None = None) -> list[Categoria]:
    return categoria_repository.listar(db=db)


def obtener_categoria(categoria_id: int, db: Session | None = None) -> Categoria:
    categoria = categoria_repository.obtener(categoria_id, db=db)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")
    return categoria


def crear_categoria(datos: CategoriaCreate, db: Session | None = None) -> Categoria:
    categoria_existente = categoria_repository.obtener_por_nombre(datos.nombre, db=db)
    if categoria_existente is not None:
        raise ConflictoError(f"Ya existe una categoría con el nombre '{datos.nombre}'.")

    categoria = Categoria(
        id=0,
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        activa=True,
    )
    return categoria_repository.guardar(categoria, db=db)


def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate, db: Session | None = None) -> Categoria:
    categoria = categoria_repository.obtener(categoria_id, db=db)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")

    if datos.nombre is not None:
        otra_categoria = categoria_repository.obtener_por_nombre(datos.nombre, db=db)
        if otra_categoria is not None and otra_categoria.id != categoria_id:
            raise ConflictoError(f"Ya existe otra categoría con el nombre '{datos.nombre}'.")
        categoria.nombre = datos.nombre

    if datos.descripcion is not None:
        categoria.descripcion = datos.descripcion

    if datos.activa is not None:
        if datos.activa:
            categoria.activar()
        else:
            categoria.desactivar()

    if datos.orden_prioridad is not None:
        categoria.orden_prioridad = datos.orden_prioridad

    categoria_repository.actualizar(categoria_id, categoria, db=db)
    return categoria


def eliminar_categoria(categoria_id: int, db: Session | None = None) -> None:
    categoria = categoria_repository.obtener(categoria_id, db=db)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")

    if habito_repository.existe_por_categoria(categoria_id, db=db):
        raise ReglaNegocioError("No se puede eliminar la categoría porque tiene hábitos asociados.")

    categoria_repository.eliminar(categoria_id, db=db)
