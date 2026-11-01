from sqlalchemy.orm import Session

from app.domain.exceptions import ConflictoError, RecursoNoEncontradoError, ReglaNegocioError
from app.domain.habito import EstadoHabito, Habito
from app.infrastructure.repositories import categoria_repository, habito_repository, usuario_repository
from app.presentation.schemas.habito_schema import HabitoCreate, HabitoUpdate


def crear_habito(datos: HabitoCreate, db: Session | None = None) -> Habito:
    if not usuario_repository.existe(datos.usuario_id, db=db):
        raise RecursoNoEncontradoError("Usuario no encontrado.")

    categoria = categoria_repository.obtener(datos.categoria_id, db=db)
    if categoria is None:
        raise RecursoNoEncontradoError("Categoría no encontrada.")

    if not categoria.activa:
        raise ReglaNegocioError("No se puede asociar un hábito a una categoría inactiva.")

    habitos_usuario = habito_repository.listar_por_usuario(datos.usuario_id, db=db)
    if any(h.nombre.casefold() == datos.nombre.casefold() for h in habitos_usuario):
        raise ConflictoError("El hábito con este nombre ya existe para este usuario.")

    habito = Habito(
        id=0,
        usuario_id=datos.usuario_id,
        categoria_id=datos.categoria_id,
        nombre=datos.nombre,
        frecuencia_semanal=datos.frecuencia_semanal,
    )
    return habito_repository.guardar(habito, db=db)


def listar_habitos_paginado(
    usuario_id: int | None = None,
    categoria_id: int | None = None,
    estado: str | None = None,
    ordenar_por: str | None = None,
    orden: str | None = None,
    direccion: str = "asc",
    pagina: int = 1,
    limite: int | None = None,
    tamano_pagina: int | None = None,
    db: Session | None = None,
) -> dict:
    cant_limite = limite if limite is not None else (tamano_pagina if tamano_pagina is not None else 10)
    criterio_orden = ordenar_por or orden or "nombre"

    if pagina < 1:
        raise ReglaNegocioError("pagina debe ser mayor o igual a 1.")

    if cant_limite < 1 or cant_limite > 100:
        raise ReglaNegocioError("limite (o tamano_pagina) debe estar entre 1 y 100.")

    dir_limpia = str(direccion).strip().lower()
    if dir_limpia not in {"asc", "desc"}:
        raise ReglaNegocioError("direccion debe ser 'asc' o 'desc'.")

    if criterio_orden not in {"nombre", "frecuencia_semanal", "fecha_creacion"}:
        raise ReglaNegocioError("El orden debe ser nombre, frecuencia_semanal o fecha_creacion.")

    if estado is not None:
        estado_limpio = estado.strip().upper()
        if estado_limpio not in {"ACTIVO", "PAUSADO", "ARCHIVADO"}:
            raise ReglaNegocioError(f"Estado '{estado}' no es válido.")
        estado_filtro = estado_limpio
    else:
        estado_filtro = None

    items, total, total_paginas = habito_repository.buscar_paginado(
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        estado=estado_filtro,
        ordenar_por=criterio_orden,
        direccion=dir_limpia,
        pagina=pagina,
        limite=cant_limite,
        db=db,
    )

    return {
        "items": items,
        "total": total,
        "pagina": pagina,
        "limite": cant_limite,
        "total_paginas": total_paginas,
    }


def obtener_habito(habito_id: int, db: Session | None = None) -> Habito:
    habito = habito_repository.obtener(habito_id, db=db)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")
    return habito


def actualizar_habito(habito_id: int, datos: HabitoUpdate, db: Session | None = None) -> Habito:
    habito = habito_repository.obtener(habito_id, db=db)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")

    if datos.nombre is not None:
        habitos_usuario = habito_repository.listar_por_usuario(habito.usuario_id, db=db)
        if any(h.nombre.casefold() == datos.nombre.casefold() and h.id != habito_id for h in habitos_usuario):
            raise ConflictoError("El hábito con este nombre ya existe para este usuario.")
        habito.nombre = datos.nombre

    if datos.frecuencia_semanal is not None:
        habito.frecuencia_semanal = datos.frecuencia_semanal

    if datos.categoria_id is not None:
        categoria = categoria_repository.obtener(datos.categoria_id, db=db)
        if categoria is None:
            raise RecursoNoEncontradoError("Categoría no encontrada.")
        if not categoria.activa:
            raise ReglaNegocioError("No se puede asociar un hábito a una categoría inactiva.")
        habito.categoria_id = datos.categoria_id

    if datos.estado is not None:
        habito.estado = datos.estado

    return habito_repository.actualizar(habito_id, habito, db=db)


def eliminar_habito(habito_id: int, db: Session | None = None) -> None:
    habito = habito_repository.obtener(habito_id, db=db)
    if habito is None:
        raise RecursoNoEncontradoError("Hábito no encontrado.")

    habito.archivar()
    habito_repository.actualizar(habito_id, habito, db=db)
