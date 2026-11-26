from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

MAX_INTENTOS_FALLIDOS = 5
DURACION_BLOQUEO = timedelta(minutes=15)


def _ahora_utc() -> datetime:
    """Fecha y hora UTC sin zona, igual a como se guarda en la base de datos."""
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass
class Usuario:
    """Entidad de dominio: representa a la persona que sigue sus hábitos."""

    id: int
    name: str
    email: str
    fecha_registro: datetime = field(default_factory=datetime.now)
    zona_horaria: str = "America/Santiago"
    password_hash: str | None = None
    role: str = "usuario"
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None
    token_version: int = 0

    def esta_bloqueado(self, ahora: datetime | None = None) -> bool:
        """Indica si la cuenta tiene un bloqueo temporal vigente."""
        ahora = ahora or _ahora_utc()
        return self.bloqueado_hasta is not None and self.bloqueado_hasta > ahora

    def registrar_fallo(self, ahora: datetime | None = None) -> None:
        """Cuenta un inicio de sesión fallido y bloquea al llegar al máximo.

        Los fallos durante un bloqueo no lo extienden. Al vencer el bloqueo,
        el contador vuelve a empezar.
        """
        ahora = ahora or _ahora_utc()
        if self.esta_bloqueado(ahora):
            return
        if self.bloqueado_hasta is not None:
            self.reiniciar_intentos()
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
            self.bloqueado_hasta = ahora + DURACION_BLOQUEO

    def reiniciar_intentos(self) -> None:
        """Limpia el contador y el bloqueo (tras un inicio de sesión correcto)."""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None

    def incrementar_token_version(self) -> None:
        """Invalida los tokens emitidos con la versión anterior."""
        self.token_version += 1