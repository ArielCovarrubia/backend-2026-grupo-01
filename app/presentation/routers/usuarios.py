from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.application.services import usuario_service
from app.presentation.dependencies import get_db
from app.presentation.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioResponse,
    summary="Crear usuario",
    description="Registra un nuevo usuario en la base de datos validando que el email sea único.",
    responses={
        201: {"description": "Usuario creado exitosamente."},
        409: {"description": "El email ya está registrado."},
        422: {"description": "Datos de entrada inválidos."},
    },
)
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.crear_usuario(datos, db=db)


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    summary="Listar usuarios",
    description="Devuelve todos los usuarios registrados en el sistema.",
    responses={
        200: {"description": "Listado de usuarios obtenido correctamente."},
    },
)
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db=db)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID",
    description="Devuelve el detalle de un usuario a partir de su ID.",
    responses={
        200: {"description": "Usuario encontrado."},
        404: {"description": "Usuario no encontrado."},
    },
)
def obtener_usuario(
    usuario_id: int = Path(..., description="ID del usuario", ge=1),
    db: Session = Depends(get_db),
):
    return usuario_service.obtener_usuario(usuario_id, db=db)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Actualiza el nombre, email o zona horaria de un usuario existente.",
    responses={
        200: {"description": "Usuario actualizado exitosamente."},
        404: {"description": "Usuario no encontrado."},
        409: {"description": "El email ya está en uso por otro usuario."},
    },
)
def actualizar_usuario(
    usuario_id: int = Path(..., description="ID del usuario a actualizar", ge=1),
    datos: UsuarioUpdate = ...,
    db: Session = Depends(get_db),
):
    return usuario_service.actualizar_usuario(usuario_id, datos, db=db)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario siempre que no tenga hábitos asociados.",
    responses={
        204: {"description": "Usuario eliminado correctamente."},
        404: {"description": "Usuario no encontrado."},
        409: {"description": "Conflicto: el usuario tiene hábitos asociados."},
    },
)
def eliminar_usuario(
    usuario_id: int = Path(..., description="ID del usuario a eliminar", ge=1),
    db: Session = Depends(get_db),
):
    usuario_service.eliminar_usuario(usuario_id, db=db)
