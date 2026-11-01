from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.application.services import habito_service
from app.presentation.dependencies import get_db
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


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=HabitoResponse,
    summary="Crear hábito",
    description="Crea un hábito asociado a un usuario y una categoría existentes y activos.",
    responses={
        201: {"description": "Hábito creado exitosamente."},
        400: {"description": "Violación de regla de negocio (ej. categoría inactiva)."},
        404: {"description": "Usuario o categoría no encontrados."},
        409: {"description": "El hábito con ese nombre ya existe para el usuario."},
    },
)
def crear_habito(datos: HabitoCreate, db: Session = Depends(get_db)):
    return habito_service.crear_habito(datos, db=db)


@router.get(
    "/",
    response_model=HabitoPaginadoResponse,
    summary="Listar hábitos con filtros, ordenamiento y paginación",
    description="Devuelve la colección paginada de hábitos permitiendo filtrar por usuario, categoría y estado, ordenar por atributos permitidos y paginar con metadatos según el punto 5.5 de la rúbrica.",
    responses={
        200: {"description": "Colección paginada de hábitos con metadatos."},
        400: {"description": "Parámetro de paginación, dirección u orden inválido."},
    },
)
def listar_habitos(
    usuario_id: int | None = Query(None, description="Filtrar por ID de usuario"),
    categoria_id: int | None = Query(None, description="Filtrar por ID de categoría"),
    estado: str | None = Query(None, description="Filtrar por estado (ACTIVO, PAUSADO, ARCHIVADO)"),
    ordenar_por: str | None = Query(None, description="Atributo para ordenar: nombre, frecuencia_semanal, fecha_creacion"),
    orden: str | None = Query(None, description="Alias compatible de ordenar_por"),
    direccion: str = Query("asc", description="Dirección del ordenamiento: asc o desc"),
    pagina: int = Query(1, description="Número de página (comienza en 1)"),
    limite: int | None = Query(None, description="Cantidad de elementos por página (1 a 100)"),
    tamano_pagina: int | None = Query(None, description="Alias compatible de limite"),
    db: Session = Depends(get_db),
):
    return habito_service.listar_habitos_paginado(
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        estado=estado,
        ordenar_por=ordenar_por,
        orden=orden,
        direccion=direccion,
        pagina=pagina,
        limite=limite,
        tamano_pagina=tamano_pagina,
        db=db,
    )


@router.get(
    "/{habito_id}",
    response_model=HabitoResponse,
    summary="Obtener hábito por ID",
    description="Devuelve el detalle de un hábito por su identificador.",
    responses={
        200: {"description": "Hábito encontrado."},
        404: {"description": "Hábito no encontrado."},
    },
)
def obtener_habito(
    habito_id: int = Path(..., description="ID del hábito", ge=1),
    db: Session = Depends(get_db),
):
    return habito_service.obtener_habito(habito_id, db=db)


@router.put(
    "/{habito_id}",
    response_model=HabitoResponse,
    summary="Actualizar hábito",
    description="Modifica los datos editables de un hábito (nombre, frecuencia, categoría o estado).",
    responses={
        200: {"description": "Hábito actualizado exitosamente."},
        400: {"description": "Regla de negocio inválida."},
        404: {"description": "Hábito o categoría no encontrados."},
        409: {"description": "Nombre duplicado para este usuario."},
    },
)
def actualizar_habito(
    habito_id: int = Path(..., description="ID del hábito a actualizar", ge=1),
    datos: HabitoUpdate = ...,
    db: Session = Depends(get_db),
):
    return habito_service.actualizar_habito(habito_id, datos, db=db)


@router.delete(
    "/{habito_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o archivar hábito",
    description="Archiva un hábito aplicando soft-delete para conservar el historial de cumplimiento.",
    responses={
        204: {"description": "Hábito archivado exitosamente."},
        404: {"description": "Hábito no encontrado."},
    },
)
def eliminar_habito(
    habito_id: int = Path(..., description="ID del hábito a archivar", ge=1),
    db: Session = Depends(get_db),
):
    habito_service.eliminar_habito(habito_id, db=db)
