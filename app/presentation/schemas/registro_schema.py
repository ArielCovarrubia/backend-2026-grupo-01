from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RegistroHabitoCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "habito_id": 1,
                    "fecha_registro": "2026-11-01",
                    "completado": True,
                    "valor_medido": 2.0,
                    "nota": "Meta cumplida",
                }
            ]
        },
    )
    habito_id: int
    fecha_registro: date
    completado: bool = True
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, min_length=1, max_length=200)


class RegistroHabitoUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{"completado": False, "valor_medido": 1.0, "nota": "Solo cumplí la mitad"}]
        },
    )
    completado: bool | None = None
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, min_length=1, max_length=200)


class RegistroHabitoResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "habito_id": 1,
                    "fecha_registro": "2026-11-01",
                    "completado": True,
                    "valor_medido": 2.0,
                    "nota": "Meta cumplida",
                    "creado_en": "2026-11-02T10:30:00",
                }
            ]
        }
    )

    id: int
    habito_id: int
    fecha_registro: date
    completado: bool
    valor_medido: float | None
    nota: str | None
    creado_en: datetime