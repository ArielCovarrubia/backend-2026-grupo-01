from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.infrastructure.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now, nullable=False)

