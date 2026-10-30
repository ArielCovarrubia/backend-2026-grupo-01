from fastapi import APIRouter

from app.application.services import usuario_service
from app.presentation.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.post("/", status_code=201, response_model=UsuarioResponse)
def crear_usuario(datos: UsuarioCreate):
    return usuario_service.crear_usuario(datos)


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios():
    return usuario_service.listar_usuarios()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int):
    return usuario_service.obtener_usuario(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate):
    return usuario_service.actualizar_usuario(usuario_id, datos)


@router.delete("/{usuario_id}", status_code=204)
def eliminar_usuario(usuario_id: int):
    usuario_service.eliminar_usuario(usuario_id)

