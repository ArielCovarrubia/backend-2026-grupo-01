from app.domain.categoria import Categoria
from app.infrastructure.models.categoria_model import CategoriaModel


def categoria_a_dominio(model: CategoriaModel) -> Categoria:
    return Categoria(
        id=model.id,
        nombre=model.nombre,
        descripcion=model.descripcion,
        activa=model.activa,
    )


def categoria_a_modelo(entity: Categoria) -> CategoriaModel:
    return CategoriaModel(
        id=entity.id if entity.id != 0 else None,
        nombre=entity.nombre,
        descripcion=entity.descripcion,
        activa=entity.activa,
    )

