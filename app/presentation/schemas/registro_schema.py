from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RegistroHabitoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    habito_id: int
    fecha_registro: date
    completado: bool = True
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, min_length=1, max_length=200)


class RegistroHabitoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    completado: bool | None = None
    valor_medido: float | None = Field(default=None, ge=0)
    nota: str | None = Field(default=None, min_length=1, max_length=200)


class RegistroHabitoResponse(BaseModel):
    id: int
    habito_id: int
    fecha_registro: date
    completado: bool
    valor_medido: float | None
    nota: str | None
    creado_en: datetime