from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.database import Base


class PasswordResetTokenModel(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    expira_en = Column(DateTime, nullable=False)
    usado_en = Column(DateTime, nullable=True)
