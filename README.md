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

La distribución se actualizó para trabajar con tres integrantes. La salida de Josefa no elimina sus aportes ya integrados: el mantenimiento de dominio y esquemas queda a cargo de Beatriz, mientras que Ariel asume también los repositorios y su conexión con la base de datos. Patricio conserva QA y agrega la matriz de aceptación para que cada requisito tenga una prueba asociada.

Área o archivo | Responsable principal | Apoyo y revisión |
| --- | --- | --- |
| `app/domain/` y `app/presentation/schemas/` | Beatriz | Ariel revisa compatibilidad con services |
| `app/infrastructure/` (BD, modelos, mappers) | Beatriz | Ariel valida integración ORM |
| `app/infrastructure/repositories/` y `app/application/services/` | Ariel | Beatriz revisa consistencia de datos |
| `app/presentation/routers/` y `app/main.py` | Ariel | Beatriz verifica registro de rutas |
| Swagger/OpenAPI | Ariel | Beatriz revisa el contrato |
| `test_manual/` | Patricio | Ariel reproduce los casos técnicos |
| `README.md` | Beatriz | Patricio revisa requisitos y enlaces |

### Plan de trabajo de la etapa 2

| Tarea | Responsable | Evidencia de término |
| --- | --- | --- |
| Revisar entidades, DTOs y validaciones tras la redistribución | Beatriz | Cambios revisados en `domain/` y `presentation/schemas/` |
| Conectar los repositorios a la base de datos con SQLAlchemy | Ariel | CRUD persistente y referencias entre entidades verificados |
| Completar o mantener docstrings de cada endpoint | Ariel | Operaciones visibles y explicadas en `/docs` |
| Ejecutar la colección completa y actualizar defectos | Patricio | `postman_collection.json` y `bugs_found.md` actualizados |
| Verificar los diez criterios de evaluación y documentar pendientes | Patricio | Matriz de aceptación en este README |
| Integrar cambios y revisar README final | Beatriz | Rama `main` ejecutable desde README |

La evidencia de contribución debe mantenerse en commits separados por tarea, ramas personales y pull requests revisadas. No se deben crear commits a nombre de Josefa después de su salida.

> Asegúrese de cumplir con los requerimientos establecidos para poder llevar a cabo de forma exitosa la ejecución del proyecto.
- [uv](https://docs.astral.sh/uv/) (probado con UV 0.12.13)
- Python >= 3.14 (probado en python 3.14.7)

## Descripción breve del proyecto
Este proyecto está centralizado en solucionar la dificultad de medir el progreso del bienestar diario (ejercicio, sueño, alimentación) a causa de registros desorganizados en notas sueltas, llevándose a cabo con la ayuda de una API REST en Python y FastAPI que permite gestionar usuarios, registrar el cumplimiento diario y consultar el historial mediante filtros y paginación.

## Tecnologias utilizadas
- Python (3.14.7)
- FastAPI
- Pydantic
- Uvicorn
- SQLAlchemy (ORM)
- Alembic (Migraciones)

## Arquitectura por Capas
El proyecto implementa una estricta separación por responsabilidades para garantizar la modularidad, testeabilidad y mantenimiento:
- **Presentation (`app/presentation/`)**: Gestiona la interacción HTTP mediante `routers` y valida estructuras de entrada/salida utilizando esquemas DTO con Pydantic. Se encarga también de la inyección de dependencias de base de datos (`get_db`).
- **Application (`app/application/`)**: Contiene los `services` que coordinan la lógica de negocio y los casos de uso, conectando las peticiones HTTP con las reglas del dominio y la persistencia.
- **Domain (`app/domain/`)**: Aloja las entidades puras del dominio, enumeraciones y reglas de negocio, siendo completamente independiente del framework y de la base de datos.
- **Infrastructure (`app/infrastructure/`)**: Implementa la conexión y gestión de la base de datos con SQLAlchemy (`database.py`), los modelos ORM (`models/`), los mappers de conversión (`mappers/`), el acceso a datos (`repositories/`), los seeders iniciales (`seeders/`) y las migraciones versionadas con Alembic (`migrations/`).

## Recorrido de una Petición
Para seguir el flujo de una solicitud a través de las capas de la aplicación (ej. `GET /categorias/`):
1. **Presentación**: La solicitud llega al `router` en `app/presentation/routers/categorias.py`, validando el esquema de entrada o parámetros de consulta.
2. **Aplicación**: El router delega la ejecución al servicio correspondiente en `app/application/services/categoria_service.py`.
3. **Dominio / Lógica**: El servicio ejecuta las reglas de negocio e interactúa con las entidades de la capa de dominio.
4. **Infraestructura**: El servicio invoca al repositorio correspondiente con la sesión de base de datos que el router recibe por inyección de dependencias (`Depends(get_db)`). El repositorio consulta la base con SQLAlchemy. Los `mappers` traducen el modelo ORM al objeto de dominio, y el esquema DTO serializa la respuesta final devuelta al cliente.

## Diagrama de Clases (Dominio)
```mermaid
classDiagram
    class Usuario {
        +int id
        +string name
        +string email
        +datetime fecha_registro
        +string zona_horaria
    }
    class Categoria {
        +int id
        +string nombre
        +string descripcion
        +bool activa
        +int orden_prioridad
        +activar()
        +desactivar()
    }
    class Habito {
        +int id
        +int usuario_id
        +int categoria_id
        +string nombre
        +int frecuencia_semanal
        +EstadoHabito estado
        +datetime fecha_creacion
        +esta_activo() bool
        +archivar()
    }
    class RegistroHabito {
        +int id
        +int habito_id
        +date fecha_registro
        +bool completado
        +float valor_medido
        +string nota
        +datetime creado_en
        +es_fecha_futura() bool
    }

    Usuario "1" -- "*" Habito : posee
    Categoria "1" -- "*" Habito : categoriza
    Habito "1" -- "*" RegistroHabito : tiene
```
## Diagrama Entidad-Relación (Base de datos)
Tablas creadas por la migración `migrations/versions/858f8ea721e0_initial_schema_generation.py` a partir de los modelos ORM de `app/infrastructure/models/`.

```mermaid
erDiagram
    usuarios ||--o{ habitos : "posee"
    categorias ||--o{ habitos : "clasifica"
    habitos ||--o{ registros_habito : "registra"

    usuarios {
        INTEGER id PK
        VARCHAR(60) name "NOT NULL"
        VARCHAR(100) email UK "NOT NULL"
        DATETIME fecha_registro "NOT NULL"
        VARCHAR(50) zona_horaria "NOT NULL, default America/Santiago"
    }
    categorias {
        INTEGER id PK
        VARCHAR(30) nombre UK "NOT NULL"
        VARCHAR(200) descripcion "NOT NULL"
        BOOLEAN activa "NOT NULL, default true"
        INTEGER orden_prioridad "NOT NULL, default 1"
    }
    habitos {
        INTEGER id PK
        INTEGER usuario_id FK "usuarios.id, ON DELETE RESTRICT"
        INTEGER categoria_id FK "categorias.id, ON DELETE RESTRICT"
        VARCHAR(50) nombre "NOT NULL"
        INTEGER frecuencia_semanal "NOT NULL"
        VARCHAR(20) estado "NOT NULL, default ACTIVO"
        DATETIME fecha_creacion "NOT NULL"
    }
    registros_habito {
        INTEGER id PK
        INTEGER habito_id FK "habitos.id, ON DELETE CASCADE"
        DATE fecha_registro "NOT NULL"
        BOOLEAN completado "NOT NULL, default true"
        FLOAT valor_medido "NULL"
        VARCHAR(200) nota "NULL"
        DATETIME creado_en "NOT NULL"
    }
```

| Relación 1:N | Clave foránea | Al eliminar el padre |
| --- | --- | --- |
| Un usuario tiene muchos hábitos | `habitos.usuario_id` → `usuarios.id` | `RESTRICT`: no se puede borrar un usuario con hábitos |
| Una categoría agrupa muchos hábitos | `habitos.categoria_id` → `categorias.id` | `RESTRICT`: no se puede borrar una categoría con hábitos |
| Un hábito tiene muchos registros | `registros_habito.habito_id` → `habitos.id` | `CASCADE`: al borrar un hábito se borran sus registros |

## Estructura del proyecto
El proyecto sigue una arquitectura por capas (punto 5.6 de la guía) para evitar que las rutas contengan la lógica principal o consultas a la base de datos. Las cuatro capas se agrupan dentro del paquete `app/`.

```text
app/
  main.py                 # Crea y ensambla la API (middlewares, manejo de errores y routers)
  presentation/
    dependencies.py       # Sesión de BD e inyección de dependencias por solicitud
    routers/              # Endpoints HTTP
    schemas/              # DTO de entrada/salida y validaciones (Pydantic)
  application/
    services/             # Coordinación de casos de uso y reglas de negocio
  domain/                 # Entidades, enums, excepciones y reglas del dominio
  infrastructure/
    database.py           # Conexión y sesiones de BD (SQLAlchemy)
    models/               # Modelos ORM
    mappers/              # Conversión dominio <-> ORM
    repositories/         # Acceso y persistencia de datos
    seeders/              # Carga inicial de datos
migrations/               # Migraciones Alembic
  env.py                  # Configuración de migraciones
  versions/               # Cambios versionados del esquema
test_manual/              # Colección Postman, casos de prueba y registro de bugs
tests/                    # Pruebas automatizadas con pytest
.env.example              # Variables de entorno sin secretos
alembic.ini               # Configuración de Alembic
pyproject.toml            # Dependencias del proyecto
uv.lock                   # Versiones bloqueadas de dependencias
README.md                 # Documentación principal
```

## Ejecución del proyecto
Para ejecutar este proyecto localmente desde una copia limpia utilizando `uv`, sigue estos pasos en tu terminal:

### Clonar el repositorio y entrar a la carpeta:
```bash
git clone https://github.com/ArielCovarrubia/backend-2026-grupo-01.git
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

### Configurar la base de datos
Por defecto la API usa SQLite en el archivo `habitos.db`, que se crea en la raíz del proyecto; no se requiere instalar nada adicional. La URL se lee de la variable de entorno `DATABASE_URL` (ver `.env.example`). Para usar PostgreSQL, defínala antes de ejecutar los comandos:

- #### Sistemas Linux/macOS
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/habitos  
```
- #### Sistemas Windows `PowerShell`
```bash
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/habitos"  
```

### Aplicar migraciones (Alembic)
Crea las cuatro tablas desde cero según `migrations/versions/`:
```bash
uv run alembic upgrade head
```

Otros comandos útiles:
```bash
uv run alembic current      # ver la versión aplicada
uv run alembic downgrade base   # deshacer todas las migraciones
```

### Ejecutar seeders (carga inicial)
Inserta 3 usuarios, 3 categorías, 3 hábitos y 2 registros, con relaciones 1:N válidas. Si la base ya tiene usuarios, no vuelve a insertar datos:
```bash
uv run python -m app.infrastructure.seeders.seed
```

Para reiniciar la base desde cero (SQLite):
```bash
rm habitos.db
uv run alembic upgrade head
uv run python -m app.infrastructure.seeders.seed
```

### Ejecutar el servidor de desarrollo:
```bash
uv run uvicorn app.main:app --reload
```

## Acceso a Swagger/OpenAPPI
la aplicación queda disponible en 
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`


## Ejecución de pruebas

### Pruebas automatizadas (pytest)
```bash
uv sync --group dev
uv run pytest
```
Las pruebas usan una base SQLite temporal (definida en `tests/conftest.py`), por lo que no modifican `habitos.db`.

### Pruebas manuales (Postman)
1. Iniciar la API con migraciones y seeders aplicados.
2. Importar `test_manual/postman_collection.json` en Postman o Thunder Client.
3. Ejecutar la colección. Los casos, resultados esperados y obtenidos están en `test_manual/casos_prueba_e5.md`, y los defectos en `test_manual/bugs_found.md`.

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
| Hábitos | GET | `/habitos/` | Consultar hábitos con filtro, orden y paginación (primero filtra, luego ordena y al final pagina) | **Query**:<br>- `usuario_id` (int, opcional)<br>- `categoria_id` (int, opcional)<br>- `estado` (`ACTIVO`, `PAUSADO` o `ARCHIVADO`, opcional)<br>- `ordenar_por` (`nombre`, `frecuencia_semanal` o `fecha_creacion`; default: `nombre`)<br>- `direccion` (`asc` o `desc`; default: `asc`)<br>- `pagina` (int ≥ 1, default: 1)<br>- `limite` (int entre 1 y 100, default: 10)<br>Alias aceptados: `orden` = `ordenar_por`, `tamano_pagina` = `limite` | 200 OK<br>`HabitoPaginadoResponse` (`items`, `total`, `pagina`, `limite`, `total_paginas`) |
| Hábitos | GET | `/habitos/{habito_id}` | Obtener los detalles de un hábito específico | **Path**: `habito_id` (int) | 200 OK<br>`HabitoResponse` |
| Hábitos | PUT | `/habitos/{habito_id}` | Modificar los datos de un hábito existente | **Path**: `habito_id` (int)<br>Body: `HabitoUpdate` | 200 OK<br>`HabitoResponse` |
| Hábitos | DELETE | `/habitos/{habito_id}` | Archivar un hábito (borrado lógico: cambia su estado a `ARCHIVADO` y conserva sus registros) | **Path**: `habito_id` (int) | 204 No Content |
| Registros de Hábito | POST | `/registros/` | Crear un nuevo registro de cumplimiento para un hábito | **Body**: `RegistroHabitoCreate` | 201 Created<br>`RegistroHabitoResponse` |
| Registros de Hábito | GET | `/registros/` | Listar todos los registros de hábitos guardados | *Ninguno* | 200 OK<br>`list[RegistroHabitoResponse]` |
| Registros de Hábito | GET | `/registros/{registro_id}` | Obtener la información de un registro por su ID | **Path**: `registro_id` (int) | 200 OK<br>`RegistroHabitoResponse` |
| Registros de Hábito | PUT | `/registros/{registro_id}` | Actualizar los datos de un registro existente | **Path**: `registro_id` (int)<br>Body: `RegistroHabitoUpdate` | 200 OK<br>`RegistroHabitoResponse` |
| Registros de Hábito | DELETE | `/registros/{registro_id}` | Eliminar un registro de hábito | **Path**: `registro_id` (int) | 204 No Content |
| Categorías | GET | `/categorias/` | Listar todas las categorías disponibles | *Ninguno* | 200 OK<br>`list[CategoriaResponse]` |
| Categorías | POST | `/categorias/` | Crear una nueva categoría de hábitos | **Body**: `CategoriaCreate` | 201 Created<br>`CategoriaResponse` |
| Categorías | GET | `/categorias/{categoria_id}` | Obtener una categoría por su ID | **Path**: `categoria_id` (int) | 200 OK<br>`CategoriaResponse` |
| Categorías | PUT | `/categorias/{categoria_id}` | Actualizar nombre, descripción o estado de una categoría | **Path**: `categoria_id` (int)<br>**Body**: `CategoriaUpdate` | 200 OK<br>`CategoriaResponse` |
| Categorías | DELETE | `/categorias/{categoria_id}` | Eliminar una categoría sin hábitos asociados | **Path**: `categoria_id` (int) | 204 No Content |

## Estado de los criterios

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Responsabilidades asignadas para tres integrantes | Listo | Tabla de distribución anterior |
| Clonación y ejecución desde README | Listo | `uv sync`, migraciones, seeders, servidor y pruebas documentados |
| Al menos 12 endpoints identificables y ejecutables | Listo | 20 endpoints funcionales y contrato OpenAPI |
| CRUD completo para una entidad | Listo | CRUD en Usuarios, Categorías, Hábitos y Registros |
| Cuatro entidades, atributos, IDs y relación 1:N | Listo | Usuario, Categoría, Hábito y RegistroHabito con relaciones ORM |
| Validaciones y reglas de negocio | Listo | Schemas, Pydantic y Services |
| Filtrado, ordenamiento y paginación | Listo | `GET /habitos/` con `ordenar_por`, `direccion`, `pagina`, `limite` y metadatos calculados en la base de datos |
| Persistencia real y migraciones / seeders | Listo | Repositorios con SQLAlchemy, migración Alembic y seeders; caso 6 de `test_manual/casos_prueba_e5.md` |
| README completo | Listo | Instalación, arquitectura, diagramas y contrato |
| Colección importable | Listo | `test_manual/postman_collection.json` |