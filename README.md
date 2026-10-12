# Proyecto grupal: diseño e implementación de una API backend 

## Curso y grupo 

Desarrollo_de_Backend (ICINF1108) 2026 - grupo 01

## Integrantes y Responsabilidades

| Estudiante | Responsabilidad |
| --- | --- |
| Beatriz Martin | Coordinación, integración, dominio, esquemas y documentación |
| Ariel Covarrubias | API, lógica de negocio, repositorios y contrato OpenAPI |
| Patricio Salazar | Calidad, pruebas manuales y verificación de requisitos |

### Redistribución por la salida de una integrante

La distribución se actualizó para trabajar con tres integrantes. La salida de Josefa no elimina sus aportes ya integrados: el mantenimiento de dominio y esquemas queda a cargo de Beatriz, mientras que Ariel asume también los repositorios en memoria. Patricio conserva QA y agrega la matriz de aceptación para que cada requisito tenga una prueba asociada.

| Área o archivo | Responsable principal | Apoyo y revisión |
| --- | --- | --- |
| `app/domain/` y `app/schemas/` | Beatriz | Ariel revisa compatibilidad con services |
| `app/repositories/` | Ariel | Beatriz revisa el modelo de datos |
| `app/routers/` y `app/services/` | Ariel | Beatriz revisa integración |
| `app/main.py` | Beatriz | Ariel verifica registro de routers |
| Swagger/OpenAPI | Ariel | Beatriz revisa el contrato |
| `test_manual/` | Patricio | Ariel reproduce los casos técnicos |
| `README.md` | Beatriz | Patricio revisa requisitos y enlaces |

### Plan de trabajo de la etapa 2

| Tarea | Responsable | Evidencia de término |
| --- | --- | --- |
| Revisar entidades, DTOs y validaciones tras la redistribución | Beatriz | Cambios revisados en `domain/` y `schemas/` |
| Revisar repositorios y consistencia del almacenamiento en memoria | Ariel | CRUD y referencias entre entidades verificados |
| Completar o mantener docstrings de cada endpoint | Ariel | Operaciones visibles y explicadas en `/docs` |
| Ejecutar la colección completa y actualizar defectos | Patricio | `postman_collection.json` y `bugs_found.md` actualizados |
| Verificar los diez criterios de evaluación y documentar pendientes | Patricio | Matriz de aceptación en este README |
| Integrar cambios y revisar README final | Beatriz | Rama `main` ejecutable desde README |

La evidencia de contribución debe mantenerse en commits separados por tarea, ramas personales y pull requests revisadas. No se deben crear commits a nombre de Josefa después de su salida.

## Requerimientos
>asegurese de cumplir con los requerimientos establecidos para poder llevar a cabo de forma exitosa la Ejecución del proyecto
- [uv](https://docs.astral.sh/uv/) (probado con UV 0.12.13)

## Descripción breve del proyecto
Este proyecto está centralizado en solucionar la dificultad de medir el progreso del bienestar diario (ejercicio, sueño, alimentación) a causa de registros desorganizados en notas sueltas, llevándose a cabo con la ayuda de una API REST en Python y FastAPI que permite gestionar usuarios, registrar el cumplimiento diario y consultar el historial mediante filtros y paginación.

## Tecnologias utilizadas
- Python (3.14.7)
- FastAPI
- Pydantic
- Uvicorn

## Almacenamiento
En memoria mediante diccionarios

## Estructura del proyecto
El proyecto sigue una arquitectura separada por responsabilidades para evitar que las rutas contengan la lógica principal

```text
app/
  domain/           # Entidades y reglas del dominio  
  repositories/     # Almacenamiento en memoria (listas/diccionarios)
  routers/          # Definición de rutas/endpoints
  schemas/          # Definición de DTOs y validaciones de entrada/salida
  services/         # Casos de uso y lógica de negocio
  main.py           # Crea y configura la aplicación; recibe solicitudes HTTP
test_manual/        # Colección Postman y registro de bugs
pyproject.toml      # Listado de dependencias
README.md           # Documentación principal
uv.lock             # Archivo de bloqueo de versiones de dependencias

```

## Ejecución del proyecto
Para ejecutar este proyecto localmente desde una copia limpia utilizando `uv`, sigue estos pasos en tu terminal:

### Clonar el repositorio y entrar a la carpeta:
```bash
git clone https://github.com/jobbinnie/backend-2026-grupo-01.git
cd backend-2026-grupo-01
```

### Sincronizar e intalar las dependencias automáticamente con `uv`:
```bash
uv sync
```

### Activar entorno virtual del proyecto
la activación de entornos vituales depende del Shell activo de su sistema operativo, se indicaron los dos casos más comunes para sistemas linux, macOS y Windows

- #### Sistemas Linux/macOS `(Bash / Zsh / Dash / Ksh)`
```bash
source  .venv/bin/activate
```

+ si es que utiliza `fish` utilice `source venv/bin/activate.fish`
+ si es que utiliza `Csh / Tcsh` utilice `source venv/bin/activate.csh`

- #### Sistemas Windows `PowerShell (POSIX)`
```bash
.venv\Scripts\Activate.ps1
```

### Ejecutar el servidor de desarrollo:
```bash
uv run uvicorn app.main:app --reload
```

## Acceso a Swagger/OpenAPPI
la aplicación queda disponible en 
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`


### Desactivar entorno vitual del proyecto:
```bash
deactivate
```

## Contrato de endpoints
| Entidad | Método | URI | Descripción | Parámetros | Respuesta |
| --- | --- | --- | --- | --- | --- |
| Usuario | POST | `/usuarios/` | Crear un nuevo usuario en la plataforma | **Body**: `UsuarioCreate` | 201 Created<br>`UsuarioResponse` |
| Usuario | GET | `/usuarios/` | Obtener el listado completo de usuarios | *Ninguno* | 200 OK<br>`list[UsuarioResponse]` |
| Usuario | GET | `/usuarios/{usuario_id}` | Obtener la información de un usuario por su ID | **Path**: `usuario_id` (int) | 200 OK<br>`UsuarioResponse` |
| Usuario | PUT | `/usuarios/{usuario_id}` | Actualizar los datos de un usuario existente | **Path**: `usuario_id` (int)<br>**Body**: `UsuarioUpdate` | 200 OK<br>`UsuarioResponse` |
| Usuario | DELETE | `/usuarios/{usuario_id}` | Eliminar un usuario del sistema | **Path**: `usuario_id` (int) | 204 No Content |
| Hábitos | POST | `/habitos/` | Registrar un nuevo hábito saludable | **Body**: `HabitoCreate` | 201 Created<br>`HabitoResponse` |
| Hábitos | GET | `/habitos/` | Consultar hábitos con opción de filtros y paginación | **Query**:<br>- `usuario_id` (int, opcional)<br>- `categoria_id` (int, opcional)<br>- `estado` (str, opcional)<br>- `orden` (str, default: "nombre")<br>- `pagina` (int, default: 1)<br>- `tamano_pagina` (int, default: 10) | 200 OK<br>`list[HabitoResponse]` |
| Hábitos | GET | `/habitos/{habito_id}` | Obtener los detalles de un hábito específico | **Path**: `habito_id` (int) | 200 OK<br>`HabitoResponse` |
| Hábitos | PUT | `/habitos/{habito_id}` | Modificar los datos de un hábito existente | **Path**: `habito_id` (int)<br>Body: `HabitoUpdate` | 200 OK<br>`HabitoResponse` |
| Hábitos | DELETE | `/habitos/{habito_id}` | Eliminar un hábito | **Path**: `habito_id` (int) | 204 No Content |
| Registros de Hábito | POST | `/registros/` | Crear un nuevo registro de cumplimiento para un hábito | **Body**: `RegistroHabitoCreate` | 201 Created<br>`RegistroHabitoResponse` |
| Registros de Hábito | GET | `/registros/` | Listar todos los registros de hábitos guardados | *Ninguno* | 200 OK<br>`list[RegistroHabitoResponse]` |
| Registros de Hábito | GET | `/registros/{registro_id}` | Obtener la información de un registro por su ID | **Path**: `registro_id` (int) | 200 OK<br>`RegistroHabitoResponse` |
| Registros de Hábito | PUT | `/registros/{registro_id}` | Actualizar los datos de un registro existente | **Path**: `registro_id` (int)<br>Body: `RegistroHabitoUpdate` | 200 OK<br>`RegistroHabitoResponse` |
| Registros de Hábito | DELETE | `/registros/{registro_id}` | Eliminar un registro de hábito | **Path**: `registro_id` (int) | 204 No Content |
| Categorías | GET | `/categorias/` | Listar todas las categorías disponibles | *Ninguno* | 200 OK<br>`list[CategoriaResponse]` |
| Categorías | POST | `/categorias/` | Crear una nueva categoría de hábitos | **Body**: `CategoriaCreate` | 201 Created<br>`CategoriaResponse` |

## Estado de los criterios

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Responsabilidades asignadas para tres integrantes | Listo | Tabla de distribución anterior |
| Clonación y ejecución desde README | Listo | `uv sync` y `uv run uvicorn app.main:app --reload` |
| Al menos 12 endpoints identificables y ejecutables | Listo | Contrato de 17 endpoints y colección Postman |
| CRUD completo para una entidad | Listo | Usuarios: POST, GET, GET por ID, PUT y DELETE |
| Cuatro entidades, atributos, IDs y relación 1:N | Listo | Usuario, Categoría, Hábito y RegistroHabito |
| Validaciones y reglas de negocio | Listo | Schemas y services; casos en QA |
| Filtrado, ordenamiento y paginación | Listo | `GET /habitos/`, en ese orden |
| Almacenamiento en memoria y sin credenciales reales | Listo | Repositorios basados en diccionarios |
| README completo | Listo | Instalación, estructura, equipo y contrato |
| Colección importable | Listo | `test_manual/postman_collection.json` |
| Evidencia Git de los tres integrantes actuales | Pendiente de verificar | Commits, ramas y pull requests de la etapa 2 |