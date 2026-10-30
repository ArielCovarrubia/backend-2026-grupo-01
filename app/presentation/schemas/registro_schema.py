from datetime import date, datetime

from pydantic import BaseModel, Field


class RegistroHabitoCreate(BaseModel):
    habito_id: int
    fecha_registro: date
    completado: bool = True
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, max_length=200)


class RegistroHabitoUpdate(BaseModel):
    completado: bool | None = None
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, max_length=200)


class RegistroHabitoResponse(BaseModel):
    id: int
    habito_id: int
    fecha_registro: date
    completado: bool
    valor_medido: float | None
    nota: str | None
    creado_en: datetime

