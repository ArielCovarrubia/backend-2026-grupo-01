from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.habito import EstadoHabito


class HabitoCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "usuario_id": 1,
                    "categoria_id": 1,
                    "nombre": "Dormir 8 horas",
                    "frecuencia_semanal": 7,
                }
            ]
        },
    )

    usuario_id: int
    categoria_id: int
    nombre: str = Field(..., min_length=3, max_length=50)
    frecuencia_semanal: int = Field(..., ge=1, le=7)


class HabitoUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"examples": [{"frecuencia_semanal": 5, "estado": "PAUSADO"}]},
    )

    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    frecuencia_semanal: int | None = Field(default=None, ge=1, le=7)
    categoria_id: int | None = None
    estado: EstadoHabito | None = None


class HabitoResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "usuario_id": 1,
                    "categoria_id": 1,
                    "nombre": "Beber 2 litros de agua",
                    "frecuencia_semanal": 7,
                    "estado": "ACTIVO",
                    "fecha_creacion": "2026-11-02T10:30:00",
                }
            ]
        }
    )

    id: int
    usuario_id: int
    categoria_id: int
    nombre: str
    frecuencia_semanal: int
    estado: EstadoHabito
    fecha_creacion: datetime


class HabitoPaginadoResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "id": 1,
                            "usuario_id": 1,
                            "categoria_id": 1,
                            "nombre": "Beber 2 litros de agua",
                            "frecuencia_semanal": 7,
                            "estado": "ACTIVO",
                            "fecha_creacion": "2026-11-02T10:30:00",
                        }
                    ],
                    "total": 2,
                    "pagina": 2,
                    "limite": 1,
                    "total_paginas": 2,
                }
            ]
        }
    )

    items: list[HabitoResponse]
    total: int
    pagina: int
    limite: int
    total_paginas: int

