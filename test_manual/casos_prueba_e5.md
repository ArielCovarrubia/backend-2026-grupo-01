# Casos de prueba obligatorios (Entregable E5)

Fecha de ejecución: 1 de noviembre de 2026, sobre `main` con los repositorios conectados a la base de datos (PR #40).
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
| 6 | Persistencia tras reinicio | Aprobado |

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
| Solicitud | `GET /habitos/?pagina=2&limite=3` con 4 hábitos creados |
| Entrada | Parámetros `usuario_id`, `categoria_id`, `estado`, `ordenar_por` (`nombre`, `frecuencia_semanal`, `fecha_creacion`), `direccion` (`asc` o `desc`), `pagina` y `limite` (1 a 100). Los nombres antiguos `orden` y `tamano_pagina` siguen funcionando como alias. Pruebas inválidas: `pagina=0`, `limite=101`, `direccion=arriba`, `ordenar_por=color` y `estado=xyz` |
| Resultado esperado | 200 con `{"items": [...], "total": 4, "pagina": 2, "limite": 3, "total_paginas": 2}` y un solo elemento en `items`. Los filtros y el orden reducen y ordenan la lista. Los parámetros inválidos responden 400 |
| Resultado obtenido | 200 con `total` 4, `pagina` 2, `limite` 3, `total_paginas` 2 y 1 elemento. Filtros, orden ascendente y descendente correctos. Todos los parámetros inválidos responden 400 con `BUSINESS_RULE_ERROR` |
| Estado | Aprobado |

## Caso 6: Persistencia tras reinicio

| | Detalle |
| --- | --- |
| Procedimiento | 1. Base nueva con `alembic upgrade head` y seeders. 2. Levantar el servidor. 3. `GET /usuarios/` y `GET /categorias/1`. 4. `POST /usuarios/` con `{"name": "Persistente", "email": "persist@x.cl"}`. 5. Detener el servidor con Ctrl+C. 6. Volver a levantarlo. 7. `GET /usuarios/` |
| Resultado esperado | Los 3 usuarios del seeder son visibles desde el inicio y, después del reinicio, también sigue apareciendo el usuario "Persistente" |
| Resultado obtenido | En el paso 3, `GET /usuarios/` devuelve los 3 usuarios del seeder y `GET /categorias/1` responde 200. Tras el reinicio, `GET /usuarios/` devuelve los 4 usuarios, incluido "Persistente" |
| Estado | Aprobado |

Historial: el 31 de octubre este caso salió reprobado (bug 13), porque los repositorios guardaban los datos en diccionarios en memoria. Se repitió después del PR #40 y pasó. La prueba automatizada `tests/test_persistencia.py` reinicia un servidor real y verifica lo mismo.
