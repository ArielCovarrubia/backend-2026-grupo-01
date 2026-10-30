from datetime import date

from app.domain.registro_habito import RegistroHabito

_registros: dict[int, RegistroHabito] = {}
_contador_id = 0


def guardar(registro: RegistroHabito) -> RegistroHabito:
    global _contador_id
    _contador_id += 1
    registro.id = _contador_id
    _registros[registro.id] = registro
    return registro


def listar() -> list[RegistroHabito]:
    return list(_registros.values())


def obtener(registro_id: int) -> RegistroHabito | None:
    return _registros.get(registro_id)


def listar_por_habito(habito_id: int) -> list[RegistroHabito]:
    return [r for r in _registros.values() if r.habito_id == habito_id]


def existe_registro_en_fecha(habito_id: int, fecha: date) -> bool:
    return any(
        r.habito_id == habito_id and r.fecha_registro == fecha
        for r in _registros.values()
    )


def actualizar(registro_id: int, registro: RegistroHabito) -> RegistroHabito | None:
    if registro_id not in _registros:
        return None
    registro.id = registro_id
    _registros[registro_id] = registro
    return registro


def eliminar(registro_id: int) -> bool:
    return _registros.pop(registro_id, None) is not None


def existe(registro_id: int) -> bool:
    return registro_id in _registros

