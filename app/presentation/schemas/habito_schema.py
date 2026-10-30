from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.habito import EstadoHabito


class HabitoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    usuario_id: int
    categoria_id: int
    nombre: str = Field(..., min_length=3, max_length=50)
    frecuencia_semanal: int = Field(..., ge=1, le=7)


class HabitoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    frecuencia_semanal: int | None = Field(default=None, ge=1, le=7)
    categoria_id: int | None = None
    estado: EstadoHabito | None = None


class HabitoResponse(BaseModel):
    id: int
    usuario_id: int
    categoria_id: int
    nombre: str
    frecuencia_semanal: int
    estado: EstadoHabito
    fecha_creacion: datetime


class HabitoPaginadoResponse(BaseModel):
    items: list[HabitoResponse]
    total: int
    pagina: int
    limite: int
    total_paginas: int

