import os

from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError
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
from app.presentation.routers import (
    auth,
    categorias,
    habitos,
    health,
    registros,
    usuarios,
)

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
        origen.strip()
        for origen in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origen.strip()
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


@app.exception_handler(IntegrityError)
async def integrity_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "CONFLICT",
                "message": "El recurso entra en conflicto con datos existentes.",
                "details": [],
            }
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Error interno del servidor.",
                "details": [],
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
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(habitos.router)
app.include_router(registros.router)
app.include_router(health.router)


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

ESQUEMA_SEGURIDAD = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

EJEMPLOS_ERROR = {
    "401": {
        "error": {
            "code": "HTTP_ERROR",
            "message": "Credenciales requeridas.",
            "details": [],
        }
    },
    "403": {
        "error": {
            "code": "HTTP_ERROR",
            "message": "No tienes permiso para operar sobre este recurso.",
            "details": [],
        }
    },
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
    "503": {
        "error": {
            "code": "HTTP_ERROR",
            "message": "Base de datos no disponible.",
            "details": [],
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
    esquema["components"]["securitySchemes"] = ESQUEMA_SEGURIDAD
    rutas_publicas = {
        "/health",
        "/auth/login",
        "/auth/refresh",
        "/auth/forgot-password",
        "/auth/reset-password",
        "/usuarios/",
    }
    for ruta, operaciones in esquema["paths"].items():
        for metodo, operacion in operaciones.items():
            if metodo.lower() in {"get", "post", "put", "delete", "patch"}:
                publicacion = ruta in rutas_publicas
                if ruta == "/auth/logout":
                    publicacion = True
                if not publicacion:
                    operacion.setdefault("security", [{"bearerAuth": []}])
                if "401" not in operacion["responses"] and not publicacion:
                    operacion["responses"]["401"] = {"description": "Credenciales requeridas o token inválido."}
                if "403" not in operacion["responses"] and not publicacion:
                    operacion["responses"]["403"] = {"description": "Permisos insuficientes."}
                operacion["responses"].setdefault("500", {"description": "Error interno del servidor."})
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
