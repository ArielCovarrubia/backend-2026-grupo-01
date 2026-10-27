from dataclasses import dataclass

@dataclass
class Categoria:
    """Entidad de dominio: clasifica los hábitos (SALUD, EJERCICIO, etc.)"""
    id: int
    nombre: str
    descripcion: str
    activa: bool = True 

    def activar(self) -> None:
        """Método de dominio para activar la categoría."""
        self.activa = True

    def desactivar(self) -> None:
        """Método de dominio para desactivar la categoría."""
        self.activa = False