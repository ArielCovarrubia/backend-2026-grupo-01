from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base

class CategoriaModel(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(30), unique=True, index=True, nullable=False)
    descripcion = Column(String(200), nullable=False)
    activa = Column(Boolean, default=True, nullable=False)
    orden_prioridad = Column(Integer, default=1, nullable=False)
    habitos = relationship("HabitoModel", back_populates="categoria")