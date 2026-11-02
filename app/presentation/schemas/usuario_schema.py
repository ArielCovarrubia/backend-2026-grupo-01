from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"examples": [{"name": "Ana Pérez", "email": "ana.perez@uct.cl"}]},
    )

    name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"examples": [{"name": "Ana María Pérez"}]},
    )

    name: str | None = Field(default=None, min_length=2, max_length=60)
    email: EmailStr | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 4,
                    "name": "Ana Pérez",
                    "email": "ana.perez@uct.cl",
                    "fecha_registro": "2026-11-02T10:30:00",
                    "zona_horaria": "America/Santiago",
                }
            ]
        }
    )

    id: int
    name: str
    email: EmailStr
    fecha_registro: datetime
    zona_horaria: str  
