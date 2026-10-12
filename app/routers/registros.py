from fastapi import APIRouter

from app.schemas.registro_schema import (
    RegistroHabitoCreate,
    RegistroHabitoResponse,
    RegistroHabitoUpdate,
)
from app.services import registro_service

router = APIRouter(
    prefix="/registros",
    tags=["Registros"]
)


@router.post("/", status_code=201, response_model=RegistroHabitoResponse)
def crear_registro_habito(datos: RegistroHabitoCreate):
    """Crea un registro de cumplimiento para un hábito existente."""
    return registro_service.crear_registro_habito(datos)


@router.get("/", response_model=list[RegistroHabitoResponse])
def listar_registros_habito():
    """Devuelve todos los registros de hábitos almacenados."""
    return registro_service.listar_registros_habito()


@router.get("/{registro_id}", response_model=RegistroHabitoResponse)
def obtener_registro_habito(registro_id: int):
    """Devuelve un registro por su identificador."""
    return registro_service.obtener_registro_habito(registro_id)


@router.put("/{registro_id}", response_model=RegistroHabitoResponse)
def actualizar_registro_habito(registro_id: int, datos: RegistroHabitoUpdate):
    """Actualiza los datos editables de un registro."""
    return registro_service.actualizar_registro_habito(registro_id, datos)


@router.delete("/{registro_id}", status_code=204)
def eliminar_registro_habito(registro_id: int):
    """Elimina un registro por su identificador."""
    registro_service.eliminar_registro_habito(registro_id)