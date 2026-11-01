from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=3, max_length=30)
    descripcion: str = Field(..., max_length=200)
    orden_prioridad: int = 1


class CategoriaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(None, min_length=3, max_length=30)
    descripcion: str | None = Field(None, max_length=200)
    activa: bool | None = None
    orden_prioridad: int | None = None


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    activa: bool
    orden_prioridad: int
