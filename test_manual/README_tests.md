# QA & Testing Strategy — Pruebas Manuales Backend

Este directorio contiene los artefactos de calidad, suites de prueba manuales y reportes de defectos producidos durante el aseguramiento de calidad (QA) de la API REST del Proyecto Grupal 01.

**Responsable de QA:** Patricio Salazar

---

## Contenido de la Carpeta

- **`postman_collection.json`**: Colección ejecutable en Postman (Collection v2.1), de principio a fin, ordenada según las relaciones: usuario, categoría, hábito, registro, casos de error (404/409/422) y eliminación. Usa variables de colección (`base_url`, `usuario_id`, `categoria_id`, ...) que se llenan automáticamente.
- **`bugs_found.md`**: Registro detallado de defectos e incidencias (Defect Tracking Log) identificados durante la ejecución de pruebas REST, especificando comportamiento esperado, comportamiento obtenido, análisis técnico y estado de resolución.

---

## Preparación del Entorno de Pruebas

Para asegurar la ejecución correcta de las suites de prueba, levante el entorno de desarrollo mediante los comandos de entorno virtual o el runner de `uv`:

```bash
# Opción 1: Vía ejecutable uv (Recomendado)
uv run uvicorn app.main:app --reload

# Opción 2: Activación previa del entorno virtual
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\Activate.ps1   # Windows
uvicorn app.main:app --reload

---

## Pruebas automatizadas (`tests/`)

```bash
uv sync --group dev
uv run pytest
```

- `conftest.py`: fixtures que vacían los diccionarios en memoria y reinician los contadores de ID antes y después de cada prueba, además de fixtures para crear usuario, categoría, hábito y registro.
- `test_usuarios.py`, `test_categorias.py`, `test_habitos.py`, `test_registros.py`: CRUD, duplicados (409), fecha futura, IDs inexistentes (404), validaciones (422), filtros, ordenamiento y paginación.
- `test_cors.py`: preflight y cabeceras CORS para `http://localhost:5173`.
- `test_bugs_conocidos.py`: pruebas `xfail` de los bugs documentados en `bugs_found.md`.
