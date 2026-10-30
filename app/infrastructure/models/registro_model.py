from datetime import date, datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from app.infrastructure.database import Base


class RegistroHabitoModel(Base):
    __tablename__ = "registros_habito"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    habito_id = Column(Integer, ForeignKey("habitos.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_registro = Column(Date, default=date.today, nullable=False)
    completado = Column(Boolean, default=True, nullable=False)
    valor_medido = Column(Float, nullable=True)
    nota = Column(String(200), nullable=True)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)

