from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
 
 
class EstadoHabito(str, Enum):
    """Valores permitidos para el estado de un hábito (validación de Enum)."""
    ACTIVO = "ACTIVO"
    PAUSADO = "PAUSADO"
    ARCHIVADO = "ARCHIVADO"
 
 
@dataclass
class Habito:
    """
    Entidad de dominio: un hábito que un Usuario quiere seguir.
    Relación N:1 con Usuario y N:1 con Categoria.
    """
    id: int
    usuario_id: int
    categoria_id: int
    nombre: str
    frecuencia_semanal: int
    estado: EstadoHabito = EstadoHabito.ACTIVO
    fecha_creacion: datetime = field(default_factory=datetime.now)
 
    def esta_activo(self) -> bool:
        """Comportamiento propio del dominio: no requiere consultar otras entidades."""
        return self.estado == EstadoHabito.ACTIVO
 
    def archivar(self) -> None:
        """Cambia el estado en vez de permitir el borrado físico (regla de negocio)."""
        self.estado = EstadoHabito.ARCHIVADO

    def desarchivar(self) -> None:
        """Reactiva un hábito archivado (inverso de archivar)."""
        self.estado = EstadoHabito.ACTIVO