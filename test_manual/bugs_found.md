# Bugs Found — Pruebas manuales Backend Grupo 01

Documento de seguimiento de bugs encontrados durante las pruebas con Postman/Swagger.
Responsable de pruebas: Patricio Salazar (QA), con reproducción técnica de Ariel y revisión de integración de Beatriz.

---

## Bug 1: Rutas de Hábitos, Categorías y Registros no responden (404)

- **Estado:**  RESUELTO (confirmado en `main.py`)
- **Endpoint(s) afectado(s):** `GET/POST /habitos/`, `GET/POST /categorias/`, `GET/POST /registros/`
- **Resultado obtenido (antes del fix):** `404 Not Found`
- **Causa raíz:** `main.py` inicialmente solo incluía el router de Usuarios (`app.include_router(usuarios.router)`). Faltaban conectar los routers de Categorías, Hábitos y Registros.
- **Solución aplicada:** Se importaron e incluyeron todos los routers en `main.py` (`app.include_router(...)`).
- **Responsable:** Beatriz (main.py / integración)

---

## Bug 2: `usuarios.py` sin tipos en los parámetros del body

- **Estado:**  RESUELTO
- **Endpoint(s) afectado(s):** `POST /usuarios/`, `PUT /usuarios/{id}`
- **Resultado obtenido (antes del fix):** `422 Unprocessable Entity` — "Add missing query parameter", incluso con un body JSON válido.
- **Causa raíz:** Las funciones `crear_usuario(datos)` y `actualizar_usuario(usuario_id, datos)` no tenían tipo declarado (`datos: UsuarioCreate`), por lo que FastAPI interpretaba `datos` como query parameter en vez de body.
- **Solución aplicada:** Se agregó `usuario_schema.py` (con `UsuarioCreate`, `UsuarioUpdate`, `UsuarioResponse`) y se tipó el parámetro en el router.
- **Responsable:** Ariel (routers) + Beatriz (schemas)

---

## Bug 3: Falta dependencia `email-validator`

- **Estado:** RESUELTO
- **Síntoma:** El servidor no levantaba. Error: `ImportError: email-validator is not installed, run 'pip install pydantic[email]'`
- **Causa raíz:** `usuario_schema.py` usa el tipo `EmailStr` de Pydantic, que requiere la librería opcional `email-validator`.
- **Solución aplicada:** `uv add pydantic[email]` (o `pip install email-validator`), actualizando `pyproject.toml` / `uv.lock`.

---

## Bug 4: Desajuste de nombres entre `usuario_repository.py` y `usuario_service.py`

- **Estado:**  RESUELTO (confirmado 12/09/2026, tras merge de main a la rama psalazar)
- **Endpoint(s) afectado(s):** Todos los de Usuarios — ya verificados manualmente los 5:
  - `POST /usuarios/` → `201 Created`. Body enviado: `{"name": "Patricio", "email": "psalazar2026@alu.uct.cl"}`. Response incluye `id`, `name`, `email` y `fecha_registro` autogenerada.
  - `GET /usuarios/` → `200 OK`, devuelve el arreglo con el usuario creado.
  - `GET /usuarios/{id}` (ej. `/usuarios/1`) → `200 OK`, devuelve el usuario correcto.
  - `PUT /usuarios/{id}` → `200 OK`. Se probó actualizando `email` de `psalazar2026@alu.uct.cl` a `psalazar2026@alu.com`; el response refleja el cambio y mantiene `id` y `fecha_registro` originales.
  - `DELETE /usuarios/{id}` → `204 No Content`.
- **Causa raíz (histórica):** `usuario_service.py` importaba `usuario_repository` y llamaba a métodos `crear()`, `generar_id()`, `obtener_por_email()`, `obtener_por_id()`, pero `usuario_repository.py` solo definía funciones sueltas con nombres distintos (`guardar()`, `listar()`, `obtener()`, `actualizar()`, `eliminar()`, `existe()`), sin exponer ningún objeto `usuario_repository`. El import fallaba silenciosamente y el servicio asumía que el repositorio no existía.
- **Solución aplicada:** Se alinearon los nombres entre repositorio y servicio (confirmado funcionando end-to-end).

---

## Bug 5: Errores 422 y 404 en el endpoint `POST /registros/`

- **Estado:**  RESUELTO
- **Endpoint(s) afectado(s):** `POST /registros/`
- **Resultado obtenido (antes del fix):** 
  - `422 Unprocessable Entity`: Ocurría al omitir el campo `completado` o no cumplir el esquema de entrada (`RegistroHabitoCreate`), además del error de respuesta al faltar la inicialización del atributo `creado_en`.
  - `404 Not Found`: Ocurría por las validaciones lógicas del servicio al no existir previamente un hábito registrado en el repositorio en memoria, o por la ejecución de pruebas fuera del orden de dependencia requerido.
- **Causa raíz:**
  - El schema `RegistroHabitoCreate` exigía implícitamente `completado` como obligatorio y faltaba sincronización con los atributos exigidos por `RegistroHabitoResponse` (`creado_en`).
  - El servicio `registro_service.py` lanzaba un `404` justificado al no encontrar el `habito_id` enviado, comportamiento acentuado al reiniciar la app y perder el estado de los diccionarios en memoria.
- **Solución aplicada:**
  - Se asignó `completado: bool = True` por defecto en `RegistroHabitoCreate`.
  - Se asignó `creado_en=datetime.now()` explícitamente en la instanciación de `RegistroHabito` dentro de `registro_service.py`.
  - Se estandarizó la sintaxis del router y esquemas en alineación con las buenas prácticas del módulo de `usuarios`.
  - Se confirmó la secuencia correcta de ejecución de pruebas (`POST /usuarios/` → `POST /categorias/` → `POST /habitos/` → `POST /registros/`).
- **Responsable:** Patricio Salazar (QA) + Equipo Backend

---

## Notas generales

- El proyecto cambió su estructura de carpetas de `App/`, `Domain/`, `Repositories/` (mayúscula) a `app/`, `domain/`, `repositories/` (minúscula) durante el desarrollo. Verificar que todos los imports en el proyecto sean consistentes con la nueva convención en minúscula.
- Comando actualizado para levantar el servidor: `uvicorn app.main:app --reload` (ejecutado desde la raíz del proyecto).
- Al almacenarse los datos en estructuras en memoria (`dict`), **los datos se limpian al reiniciar el servidor**. Para realizar pruebas end-to-end completas se deben crear primero las entidades padre (`usuarios`, `categorias`) antes de crear dependientes (`habitos`, `registros`).

---

## Bugs de la etapa 2 (detectados con la colección Postman y `tests/`)

Cada bug tiene una prueba `xfail(strict=True)` en `tests/test_bugs_conocidos.py`. Cuando el bug se corrija, la prueba pasará a XPASS y fallará por `strict`, avisando que hay que quitar el marcador.

| # | Severidad | Endpoint | Esperado | Obtenido | Responsable sugerido |
| --- | --- | --- | --- | --- | --- |
| 6 | Media | `POST /usuarios/`, `PUT /usuarios/{id}` | `Ana@x.cl` y `ana@x.cl` se consideran el mismo correo (409) | Ambos se crean (201): `obtener_por_email` compara sensible a mayúsculas | Ariel (repositorio/service) |
| 7 | Alta | `DELETE /usuarios/{id}` | Rechazar (409) o eliminar en cascada | 204; los hábitos y registros del usuario quedan huérfanos y siguen visibles | Ariel |
| 8 | Baja | `POST /habitos/` | No permitir hábitos en categorías con `activa=false` | 201 | Ariel (service) |
| 9 | Baja | `POST /registros/` | No permitir registros sobre hábitos `ARCHIVADO` | 201 | Ariel (service) |
| 10 | Baja | `GET /habitos/?estado=xyz` | 400/422 por estado inválido | 200 con lista vacía (`orden` sí se valida) | Ariel |
| 11 | Baja | `POST/PUT /registros/` | `nota` de solo espacios rechazada o normalizada | Se acepta; `registro_schema.py` no tiene `str_strip_whitespace` | Beatriz (schemas) |
| 12 | Media | Todos los errores | Formato `{"detail": {"code", "message"}}` según la guía de la etapa | Se devuelve `{"error": {"code", "message", "details"}}`; hay que acordar cuál es el contrato oficial y actualizar README/pruebas | Ariel + Beatriz |

### Observaciones (no son bugs, conviene confirmarlas con el equipo)

- Eliminar una categoría con hábitos asociados responde **400** (`BUSINESS_RULE_ERROR`), no 409. Además, un hábito archivado sigue contando como "asociado", por lo que esa categoría nunca se podrá eliminar.
- Un hábito archivado bloquea volver a crear un hábito con el mismo nombre para ese usuario (409).
- `PUT /usuarios/{id}` con `{}` responde 200 sin cambios.
- `GET /categorias/` no ofrece filtros ni paginación (solo `GET /habitos/` los tiene).
- README: la tabla de contrato aún no lista `GET/PUT/DELETE /categorias/{id}`.

## Cómo se verificó

- `pytest`: 97 pruebas pasan y 7 `xfail` documentan los bugs anteriores.
- Colección Postman ejecutada completa contra `uvicorn` real: 38 solicitudes, 0 fallos. Cada solicitud guarda los IDs que crea en variables de colección y usa `{{$timestamp}}` en emails/nombres, por lo que se puede ejecutar varias veces sin reiniciar el servidor.
