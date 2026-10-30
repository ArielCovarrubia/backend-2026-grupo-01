from fastapi import APIRouter

from app.application.services import categoria_service
from app.presentation.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)


@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias():
    return categoria_service.listar_categorias()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int):
    return categoria_service.obtener_categoria(categoria_id)


@router.post("/", response_model=CategoriaResponse, status_code=201)
def crear_categoria(datos: CategoriaCreate):
    return categoria_service.crear_categoria(datos)


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate):
    return categoria_service.actualizar_categoria(categoria_id, datos)


@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int):
    categoria_service.eliminar_categoria(categoria_id)

