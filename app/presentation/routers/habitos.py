from fastapi import APIRouter

from app.application.services import habito_service
from app.presentation.schemas.habito_schema import (
    HabitoCreate,
    HabitoPaginadoResponse,
    HabitoResponse,
    HabitoUpdate,
)

router = APIRouter(
    prefix="/habitos",
    tags=["Habitos"],
)


@router.post("/", status_code=201, response_model=HabitoResponse)
def crear_habito(datos: HabitoCreate):
    return habito_service.crear_habito(datos)


@router.get("/", response_model=HabitoPaginadoResponse)
def listar_habitos(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    estado: str | None = None,
    orden: str = "nombre",
    pagina: int = 1,
    tamano_pagina: int = 10,
):
    return habito_service.listar_habitos_paginado(
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        estado=estado,
        orden=orden,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )


@router.get("/{habito_id}", response_model=HabitoResponse)
def obtener_habito(habito_id: int):
    return habito_service.obtener_habito(habito_id)


@router.put("/{habito_id}", response_model=HabitoResponse)
def actualizar_habito(habito_id: int, datos: HabitoUpdate):
    return habito_service.actualizar_habito(habito_id, datos)


@router.delete("/{habito_id}", status_code=204)
def eliminar_habito(habito_id: int):
    habito_service.eliminar_habito(habito_id)

