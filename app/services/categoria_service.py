from fastapi import HTTPException

from app.domain.categoria import Categoria
from app.repositories import categoria_repository
from app.schemas.categoria_schema import CategoriaCreate


def listar_categorias():
    return categoria_repository.listar()


def crear_categoria(datos: CategoriaCreate):
    categoria_existente = next(
        (
            categoria
            for categoria in categoria_repository.listar()
            if categoria.nombre.casefold() == datos.nombre.casefold()
        ),
        None,
    )

    if categoria_existente is not None:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una categoría con ese nombre.",
        )

    categoria = Categoria(
        id=0,
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        activa=True
    )

    return categoria_repository.guardar(categoria)
