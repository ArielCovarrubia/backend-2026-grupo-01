from app.domain.categoria import Categoria
from app.domain.exceptions import ConflictoError, RecursoNoEncontradoError, ReglaNegocioError
from app.repositories import categoria_repository, habito_repository
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate


def listar_categorias() -> list[Categoria]:
    return categoria_repository.listar()


def obtener_categoria(categoria_id: int) -> Categoria:
    categoria = categoria_repository.obtener(categoria_id)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")
    return categoria


def crear_categoria(datos: CategoriaCreate) -> Categoria:
    categoria_existente = next(
        (
            categoria
            for categoria in categoria_repository.listar()
            if categoria.nombre.casefold() == datos.nombre.casefold()
        ),
        None,
    )

    if categoria_existente is not None:
        raise ConflictoError(f"Ya existe una categoría con el nombre '{datos.nombre}'.")

    categoria = Categoria(
        id=0,
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        activa=True,
    )

    return categoria_repository.guardar(categoria)


def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate) -> Categoria:
    categoria = categoria_repository.obtener(categoria_id)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")

    if datos.nombre is not None:
        otra_categoria = next(
            (
                c
                for c in categoria_repository.listar()
                if c.nombre.casefold() == datos.nombre.casefold() and c.id != categoria_id
            ),
            None,
        )
        if otra_categoria is not None:
            raise ConflictoError(f"Ya existe otra categoría con el nombre '{datos.nombre}'.")
        categoria.nombre = datos.nombre

    if datos.descripcion is not None:
        categoria.descripcion = datos.descripcion

    if datos.activa is not None:
        if datos.activa:
            categoria.activar()
        else:
            categoria.desactivar()

    categoria_repository.actualizar(categoria_id, categoria)
    return categoria


def eliminar_categoria(categoria_id: int) -> None:
    categoria = categoria_repository.obtener(categoria_id)
    if categoria is None:
        raise RecursoNoEncontradoError(f"No existe una categoría con el ID {categoria_id}.")

    if habito_repository.existe_por_categoria(categoria_id):
        raise ReglaNegocioError("No se puede eliminar la categoría porque tiene hábitos asociados.")

    categoria_repository.eliminar(categoria_id)
