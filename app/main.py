from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import (
    ConflictoError,
    DominioException,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)
from app.routers import categorias, habitos, registros, usuarios

app = FastAPI()

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
