from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services import health_service
from app.presentation.dependencies import get_db
from app.presentation.schemas.health_schema import HealthResponse

router = APIRouter(tags=["Salud"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Comprobar disponibilidad",
    description="Ruta pública que verifica que la API y la base de datos responden.",
    responses={
        200: {"description": "API y base de datos disponibles."},
        503: {"description": "Base de datos no disponible."},
    },
)
def health(db: Session = Depends(get_db)):
    if not health_service.database_available(db):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible.",
        )
    return {"status": "ok", "database": "ok"}