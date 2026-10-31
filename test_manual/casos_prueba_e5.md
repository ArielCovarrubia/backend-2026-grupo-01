# Casos de prueba obligatorios (Entregable E5)

Fecha de ejecución: 31 de octubre de 2026.
Responsable: Patricio Salazar (Calidad y Pruebas).

Entorno: copia limpia del repositorio (rama `main`), `uv sync --group dev`, migraciones con `uv run alembic upgrade head`, seeders con `uv run python -m app.infrastructure.seeders.seed` y servidor con `uv run uvicorn app.main:app`. Base de datos por defecto: SQLite (`habitos.db`).

Todos los casos se pueden repetir con la colección `postman_collection.json` y con `uv run pytest`.

## Resumen

| Caso | Descripción | Resultado |
| --- | --- | --- |
| 1 | CRUD completo | Aprobado |
| 2 | Entrada inválida (422) | Aprobado |
| 3 | Recurso inexistente (404) | Aprobado |
| 4 | Regla de negocio (400) | Aprobado |
| 5 | Filtros, orden y paginación | Aprobado |
| 6 | Persistencia tras reinicio | Reprobado (bug 13) |

## Caso 1: CRUD completo

| | Detalle |
| --- | --- |
| Solicitudes | `POST /usuarios/`, `GET /usuarios/{id}`, `PUT /usuarios/{id}`, `DELETE /usuarios/{id}` y `GET /usuarios/{id}` (repetido para categorías, hábitos y registros) |
| Entrada | `POST /usuarios/` con `{"name": "Patricio", "email": "psalazar@alu.uct.cl"}`. Luego `PUT` con `{"name": "Patricio Salazar"}` |
| Resultado esperado | 201 con `id` y `fecha_registro`; 200 con el usuario; 200 con el nombre actualizado; 204 sin cuerpo; 404 al consultar el usuario eliminado |
| Resultado obtenido | 201 con `id` y `fecha_registro`; 200; 200 con `name` igual a "Patricio Salazar"; 204; 404 con `RESOURCE_NOT_FOUND` |
| Estado | Aprobado |

## Caso 2: Entrada inválida (422)

| | Detalle |
| --- | --- |
| Solicitud | `POST /usuarios/` |
| Entrada | `{"name": "Ana", "email": "no-es-email"}`. Variantes probadas: nombre de solo espacios, `frecuencia_semanal` igual a 9 en un hábito y `valor_medido` negativo en un registro |
| Resultado esperado | 422 con `{"error": {"code": "VALIDATION_ERROR", "message": "...", "details": [...]}}` indicando el campo inválido |
| Resultado obtenido | 422 con `code` igual a `VALIDATION_ERROR` y `details` con el campo `email`. Las tres variantes también responden 422 |
| Estado | Aprobado |

## Caso 3: Recurso inexistente (404)

| | Detalle |
| --- | --- |
| Solicitud | `GET /usuarios/99999` (también hábitos, categorías y registros) |
| Entrada | ID que no existe |
| Resultado esperado | 404 con `code` igual a `RESOURCE_NOT_FOUND` |
| Resultado obtenido | 404 con `code` igual a `RESOURCE_NOT_FOUND`. Crear un registro con `habito_id` 99999 también responde 404 |
| Estado | Aprobado |

## Caso 4: Regla de negocio (400)

| | Detalle |
| --- | --- |
| Solicitud | `POST /registros/` |
| Entrada | `{"habito_id": <id existente>, "fecha_registro": "<fecha de dentro de 5 días>"}`. Segunda prueba: `DELETE /categorias/{id}` de una categoría con hábitos asociados |
| Resultado esperado | 400 con `code` igual a `BUSINESS_RULE_ERROR` y sin crear el registro. La categoría no se elimina |
| Resultado obtenido | 400 con `code` igual a `BUSINESS_RULE_ERROR` en ambos casos. La categoría sigue existiendo |
| Estado | Aprobado |

## Caso 5: Filtros, orden y paginación

| | Detalle |
| --- | --- |
| Solicitud | `GET /habitos/?pagina=2&tamano_pagina=3` con 4 hábitos creados |
| Entrada | Parámetros `usuario_id`, `categoria_id`, `estado`, `orden` (`nombre`, `frecuencia_semanal`, `fecha_creacion`), `pagina` y `tamano_pagina`. Pruebas inválidas: `pagina=0` y `orden=color` |
| Resultado esperado | 200 con `{"items": [...], "total": 4, "pagina": 2, "limite": 3, "total_paginas": 2}` y un solo elemento en `items`. Los filtros y el orden reducen y ordenan la lista. Los parámetros inválidos responden 400 |
| Resultado obtenido | 200 con `total` 4, `pagina` 2, `limite` 3, `total_paginas` 2 y 1 elemento. Filtros y orden correctos. `pagina=0` y `orden=color` responden 400 con `BUSINESS_RULE_ERROR` |
| Estado | Aprobado |

## Caso 6: Persistencia tras reinicio

| | Detalle |
| --- | --- |
| Procedimiento | 1. Base nueva con migraciones y seeders. 2. Levantar el servidor. 3. `POST /usuarios/` con `{"name": "Persistente", "email": "persist@x.cl"}`. 4. Detener el servidor con Ctrl+C. 5. Volver a levantarlo. 6. `GET /usuarios/` |
| Resultado esperado | Después del reinicio, el usuario "Persistente" y los 3 usuarios de los seeders siguen apareciendo |
| Resultado obtenido | `GET /usuarios/` devuelve `[]` antes y después del reinicio, incluso con los seeders cargados. La tabla `usuarios` de la base sí contiene las 3 filas del seeder, pero la API no las lee. El usuario creado por la API no se guarda en la base |
| Causa | Los repositorios de `app/infrastructure/repositories/` guardan los datos en diccionarios de Python en memoria, no usan `get_db` ni los modelos SQLAlchemy |
| Estado | Reprobado. Documentado como bug 13 en `bugs_found.md` |

Este caso debe repetirse cuando los repositorios usen la base de datos.
