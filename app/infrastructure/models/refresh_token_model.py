import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.database import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)
    # Agrupa un refresh token con los que nacen de sus rotaciones
    familia_id = Column(
        String(36),
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        server_default="",
    )
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    expira_en = Column(DateTime, nullable=False)
    revocado_en = Column(DateTime, nullable=True)