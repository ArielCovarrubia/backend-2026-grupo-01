from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import (
    ConflictoError,
    DominioException,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)
from app.infrastructure.database import Base, engine
from app.infrastructure.models import (
    CategoriaModel,
    HabitoModel,
    RegistroHabitoModel,
    UsuarioModel,
)
from app.presentation.routers import categorias, habitos, registros, usuarios

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Seguimiento de Hábitos de Bienestar",
    description=(
        "API REST para registrar usuarios, categorías, hábitos y el cumplimiento diario. "
        "Todos los errores usan el formato uniforme "
        "`{\"error\": {\"code\", \"message\", \"details\"}}`."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(RecursoNoEncontradoError)
async def recurso_no_encontrado_handler(request: Request, exc: RecursoNoEncontradoError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ConflictoError)
async def conflicto_handler(request: Request, exc: ConflictoError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ReglaNegocioError)
async def regla_negocio_handler(request: Request, exc: ReglaNegocioError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(DominioException)
async def dominio_generico_handler(request: Request, exc: DominioException):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validacion_pydantic_handler(request: Request, exc: RequestValidationError):
    detalles = [
        {
            "field": ".".join(str(loc) for loc in err["loc"] if loc != "body"),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Los datos enviados no cumplen con el esquema o las validaciones declaradas.",
                "details": detalles,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": [],
            }
        },
    )


app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(habitos.router)
app.include_router(registros.router)


ESQUEMA_ERROR = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["code", "message", "details"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "details": {"type": "array", "items": {"type": "object"}},
            },
        }
    },
}

EJEMPLOS_ERROR = {
    "400": {
        "error": {
            "code": "BUSINESS_RULE_ERROR",
            "message": "No se puede eliminar la categoría porque tiene hábitos asociados.",
            "details": [],
        }
    },
    "404": {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "Usuario no encontrado.",
            "details": [],
        }
    },
    "409": {
        "error": {
            "code": "CONFLICT",
            "message": "El email ya está registrado.",
            "details": [],
        }
    },
    "422": {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Los datos enviados no son válidos.",
            "details": [{"field": "email", "message": "value is not a valid email address"}],
        }
    },
}


def generar_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    esquema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    for operaciones in esquema["paths"].values():
        for operacion in operaciones.values():
            for codigo, respuesta in operacion.get("responses", {}).items():
                if codigo in EJEMPLOS_ERROR:
                    respuesta["content"] = {
                        "application/json": {
                            "schema": ESQUEMA_ERROR,
                            "example": EJEMPLOS_ERROR[codigo],
                        }
                    }
    app.openapi_schema = esquema
    return esquema


app.openapi = generar_openapi
