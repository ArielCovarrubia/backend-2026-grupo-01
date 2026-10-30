from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now, nullable=False)
    zona_horaria = Column(String(50), default="America/Santiago", nullable=False)
    habitos = relationship("HabitoModel", back_populates="usuario", cascade="all, delete-orphan")