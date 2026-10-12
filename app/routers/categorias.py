from fastapi import APIRouter

from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaResponse,
)
from app.services import categoria_service


router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)


@router.get( "/", response_model=list[CategoriaResponse],)
def listar_categorias():
    """Devuelve todas las categorías disponibles."""
    return categoria_service.listar_categorias()


@router.post( "/", response_model=CategoriaResponse, status_code=201,)
def crear_categoria(datos: CategoriaCreate):
    """Crea una categoría nueva."""
    return categoria_service.crear_categoria(datos)