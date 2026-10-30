from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

class HabitoModel(Base):
    __tablename__ = "habitos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False, index=True)

    nombre = Column(String(50), nullable=False)
    frecuencia_semanal = Column(Integer, nullable=False)
    estado = Column(String(20), default="ACTIVO", nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)

    usuario = relationship("UsuarioModel", back_populates="habitos")
    categoria = relationship("CategoriaModel", back_populates="habitos")
    registros = relationship("RegistroHabitoModel", back_populates="habito", cascade="all, delete-orphan")
