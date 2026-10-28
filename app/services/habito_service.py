from app.domain.exceptions import ConflictoError, RecursoNoEncontradoError, ReglaNegocioError
from app.domain.habito import Habito
from app.repositories import categoria_repository, habito_repository, usuario_repository
from app.schemas.habito_schema import HabitoCreate, HabitoUpdate


def crear_habito(datos: HabitoCreate) -> Habito:
    if not usuario_repository.existe(datos.usuario_id):
        raise RecursoNoEncontradoError("Usuario no encontrado.")

    if not categoria_repository.existe(datos.categoria_id):
        raise RecursoNoEncontradoError("Categoría no encontrada.")

    habito_existente = next(
        (
            habito
            for habito in habito_repository.listar_por_usuario(datos.usuario_id)
            if habito.nombre.casefold() == datos.nombre.casefold()
        ),
        None,
    )
    if habito_existente is not None:
        raise ConflictoError("El hábito con este nombre ya existe para este usuario.")

    habito = Habito(
        id=0,
        usuario_id=datos.usuario_id,
        categoria_id=datos.categoria_id,
        nombre=datos.nombre,
        frecuencia_semanal=datos.frecuencia_semanal,
    )
    return habito_repository.guardar(habito)


def listar_habitos(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    estado: str | None = None,
    orden: str = "nombre",
    pagina: int = 1,
    tamano_pagina: int = 10,
) -> list[Habito]:
    if pagina < 1 or tamano_pagina < 1:
        raise ReglaNegocioError("pagina y tamano_pagina deben ser mayores que cero.")

    habitos = habito_repository.listar()

    if usuario_id is not None:
        habitos = [h for h in habitos if h.usuario_id == usuario_id]

    if categoria_id is not None:
        habitos = [h for h in habitos if h.categoria_id == categoria_id]

    if estado is not None:
        habitos = [h for h in habitos if h.estado.value == estado.upper()]

    if orden not in {"nombre", "frecuencia_semanal", "fecha_creacion"}:
        raise ReglaNegocioError("El orden debe ser nombre, frecuencia_semanal o fecha_creacion.")

    habitos = sorted(habitos, key=lambda habito: getattr(habito, orden))
    inicio = (pagina - 1) * tamano_pagina
    fin = inicio + tamano_pagina
    return habitos[inicio:fin]


def obtener_habito(habito_id: int) -> Habito:
    habito = habito_repository.obtener(habito_id)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")
    return habito


def actualizar_habito(habito_id: int, datos: HabitoUpdate) -> Habito:
    habito = habito_repository.obtener(habito_id)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")

    if datos.nombre is not None:
        habito_existente = next(
            (
                otro
                for otro in habito_repository.listar_por_usuario(habito.usuario_id)
                if otro.nombre.casefold() == datos.nombre.casefold()
            ),
            None,
        )
        if habito_existente and habito_existente.id != habito_id:
            raise ConflictoError("El hábito con este nombre ya existe para este usuario.")
        habito.nombre = datos.nombre

    if datos.frecuencia_semanal is not None:
        habito.frecuencia_semanal = datos.frecuencia_semanal

    if datos.categoria_id is not None:
        if not categoria_repository.existe(datos.categoria_id):
            raise RecursoNoEncontradoError("Categoría no encontrada.")
        habito.categoria_id = datos.categoria_id

    if datos.estado is not None:
        habito.estado = datos.estado

    return habito_repository.actualizar(habito_id, habito)


def eliminar_habito(habito_id: int) -> None:
    habito = habito_repository.obtener(habito_id)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")

    habito.archivar()
    habito_repository.actualizar(habito_id, habito)
