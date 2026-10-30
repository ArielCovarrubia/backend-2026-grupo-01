from fastapi import APIRouter

from app.application.services import registro_service
from app.presentation.schemas.registro_schema import (
    RegistroHabitoCreate,
    RegistroHabitoResponse,
    RegistroHabitoUpdate,
)

router = APIRouter(
    prefix="/registros",
    tags=["Registros"],
)


@router.post("/", status_code=201, response_model=RegistroHabitoResponse)
def crear_registro_habito(datos: RegistroHabitoCreate):
    return registro_service.crear_registro_habito(datos)


@router.get("/", response_model=list[RegistroHabitoResponse])
def listar_registros_habito():
    return registro_service.listar_registros_habito()


@router.get("/{registro_id}", response_model=RegistroHabitoResponse)
def obtener_registro_habito(registro_id: int):
    return registro_service.obtener_registro_habito(registro_id)


@router.put("/{registro_id}", response_model=RegistroHabitoResponse)
def actualizar_registro_habito(registro_id: int, datos: RegistroHabitoUpdate):
    return registro_service.actualizar_registro_habito(registro_id, datos)


@router.delete("/{registro_id}", status_code=204)
def eliminar_registro_habito(registro_id: int):
    registro_service.eliminar_registro_habito(registro_id)

