from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.application.services import registro_service
from app.presentation.dependencies import get_db
from app.presentation.schemas.registro_schema import (
    RegistroHabitoCreate,
    RegistroHabitoResponse,
    RegistroHabitoUpdate,
)

router = APIRouter(
    prefix="/registros",
    tags=["Registros"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistroHabitoResponse,
    summary="Crear registro de hábito",
    description="Registra el cumplimiento diario de un hábito impidiendo fechas futuras o hábitos archivados.",
    responses={
        201: {"description": "Registro de hábito creado exitosamente."},
        400: {"description": "Fecha futura o hábito archivado."},
        404: {"description": "Hábito no encontrado."},
        409: {"description": "Ya existe un registro para esta fecha."},
    },
)
def crear_registro_habito(datos: RegistroHabitoCreate, db: Session = Depends(get_db)):
    return registro_service.crear_registro_habito(datos, db=db)


@router.get(
    "/",
    response_model=list[RegistroHabitoResponse],
    summary="Listar registros de hábitos",
    description="Devuelve todos los registros de hábitos almacenados.",
    responses={
        200: {"description": "Listado de registros obtenido correctamente."},
    },
)
def listar_registros_habito(db: Session = Depends(get_db)):
    return registro_service.listar_registros_habito(db=db)


@router.get(
    "/{registro_id}",
    response_model=RegistroHabitoResponse,
    summary="Obtener registro por ID",
    description="Devuelve la información de un registro por su identificador.",
    responses={
        200: {"description": "Registro encontrado."},
        404: {"description": "Registro no encontrado."},
    },
)
def obtener_registro_habito(
    registro_id: int = Path(..., description="ID del registro", ge=1),
    db: Session = Depends(get_db),
):
    return registro_service.obtener_registro_habito(registro_id, db=db)


@router.put(
    "/{registro_id}",
    response_model=RegistroHabitoResponse,
    summary="Actualizar registro de hábito",
    description="Actualiza el estado completado, valor medido o nota de un registro.",
    responses={
        200: {"description": "Registro actualizado exitosamente."},
        404: {"description": "Registro no encontrado."},
    },
)
def actualizar_registro_habito(
    registro_id: int = Path(..., description="ID del registro a actualizar", ge=1),
    datos: RegistroHabitoUpdate = ...,
    db: Session = Depends(get_db),
):
    return registro_service.actualizar_registro_habito(registro_id, datos, db=db)


@router.delete(
    "/{registro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar registro de hábito",
    description="Elimina un registro de cumplimiento por su identificador.",
    responses={
        204: {"description": "Registro eliminado exitosamente."},
        404: {"description": "Registro no encontrado."},
    },
)
def eliminar_registro_habito(
    registro_id: int = Path(..., description="ID del registro a eliminar", ge=1),
    db: Session = Depends(get_db),
):
    registro_service.eliminar_registro_habito(registro_id, db=db)
