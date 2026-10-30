from dataclasses import dataclass, field
from datetime import datetime
 
 
@dataclass
class Usuario:
    """Entidad de dominio: representa a la persona que sigue sus hábitos."""
    id: int
    name: str
    email: str
    fecha_registro: datetime = field(default_factory=datetime.now)
    zona_horaria: str = "America/Santiago"