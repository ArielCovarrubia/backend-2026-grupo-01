from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.application.services import categoria_service
from app.presentation.dependencies import get_db
from app.presentation.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)


@router.get(
    "/",
    response_model=list[CategoriaResponse],
    summary="Listar categorías",
    description="Devuelve el listado completo de categorías disponibles.",
    responses={
        200: {"description": "Listado de categorías obtenido correctamente."},
    },
)
def listar_categorias(db: Session = Depends(get_db)):
    return categoria_service.listar_categorias(db=db)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Obtener categoría por ID",
    description="Devuelve el detalle de una categoría por su identificador.",
    responses={
        200: {"description": "Categoría encontrada."},
        404: {"description": "Categoría no encontrada."},
    },
)
def obtener_categoria(
    categoria_id: int = Path(..., description="ID de la categoría", ge=1),
    db: Session = Depends(get_db),
):
    return categoria_service.obtener_categoria(categoria_id, db=db)


@router.post(
    "/",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría de hábitos asegurando nombre único.",
    responses={
        201: {"description": "Categoría creada exitosamente."},
        409: {"description": "Ya existe una categoría con ese nombre."},
        422: {"description": "Datos de entrada inválidos."},
    },
)
def crear_categoria(datos: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_service.crear_categoria(datos, db=db)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Actualizar categoría",
    description="Actualiza los datos o el estado activo de una categoría.",
    responses={
        200: {"description": "Categoría actualizada exitosamente."},
        404: {"description": "Categoría no encontrada."},
        409: {"description": "Ya existe otra categoría con ese nombre."},
    },
)
def actualizar_categoria(
    categoria_id: int = Path(..., description="ID de la categoría a actualizar", ge=1),
    datos: CategoriaUpdate = ...,
    db: Session = Depends(get_db),
):
    return categoria_service.actualizar_categoria(categoria_id, datos, db=db)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría",
    description="Elimina una categoría del sistema siempre que no tenga hábitos asociados.",
    responses={
        204: {"description": "Categoría eliminada exitosamente."},
        400: {"description": "No se puede eliminar la categoría porque tiene hábitos asociados."},
        404: {"description": "Categoría no encontrada."},
    },
)
def eliminar_categoria(
    categoria_id: int = Path(..., description="ID de la categoría a eliminar", ge=1),
    db: Session = Depends(get_db),
):
    categoria_service.eliminar_categoria(categoria_id, db=db)
