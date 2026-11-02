from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Nutrición",
                    "descripcion": "Hábitos de alimentación saludable",
                    "orden_prioridad": 1,
                }
            ]
        },
    )

    nombre: str = Field(..., min_length=3, max_length=30)
    descripcion: str = Field(..., max_length=200)
    orden_prioridad: int = 1


class CategoriaUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{"descripcion": "Alimentación y nutrición diaria", "activa": True}]
        },
    )

    nombre: str | None = Field(None, min_length=3, max_length=30)
    descripcion: str | None = Field(None, max_length=200)
    activa: bool | None = None
    orden_prioridad: int | None = None


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 4,
                    "nombre": "Nutrición",
                    "descripcion": "Hábitos de alimentación saludable",
                    "activa": True,
                    "orden_prioridad": 1,
                }
            ]
        }
    )

    id: int
    nombre: str
    descripcion: str
    activa: bool
    orden_prioridad: int
