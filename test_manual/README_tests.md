# QA & Testing Strategy — Pruebas Manuales Backend

Este directorio contiene los artefactos de calidad, suites de prueba manuales y reportes de defectos producidos durante el aseguramiento de calidad (QA) de la API REST del Proyecto Grupal 01.

**Responsable de QA:** Patricio Salazar

---

## Contenido de la Carpeta

- **`postman_collection.json`**: Colección ejecutable en Postman (Collection v2.1) estructurada modularmente en 4 suites de prueba: *Usuarios*, *Categorías*, *Hábitos* y *Registros*.
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