from fastapi import APIRouter
from app.services import usuario_service
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/", status_code=201, response_model=UsuarioResponse)
def crear_usuario(datos: UsuarioCreate):
    """Crea un usuario nuevo y devuelve el recurso creado."""
    return usuario_service.crear_usuario(datos)


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios():
    """Devuelve todos los usuarios almacenados."""
    return usuario_service.listar_usuarios()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int):
    """Devuelve un usuario por su identificador."""
    return usuario_service.obtener_usuario(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate):
    """Actualiza los datos editables de un usuario."""
    return usuario_service.actualizar_usuario(usuario_id, datos)


@router.delete("/{usuario_id}", status_code=204)
def eliminar_usuario(usuario_id: int):
    """Elimina un usuario por su identificador."""
    usuario_service.eliminar_usuario(usuario_id)