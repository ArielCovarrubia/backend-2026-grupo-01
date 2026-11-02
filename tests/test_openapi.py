import pytest

from app.presentation.schemas import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
    HabitoCreate,
    HabitoResponse,
    HabitoUpdate,
    RegistroHabitoCreate,
    RegistroHabitoResponse,
    RegistroHabitoUpdate,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.presentation.schemas.habito_schema import HabitoPaginadoResponse

ESQUEMAS = [
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
    HabitoCreate,
    HabitoPaginadoResponse,
    HabitoResponse,
    HabitoUpdate,
    RegistroHabitoCreate,
    RegistroHabitoResponse,
    RegistroHabitoUpdate,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
]


@pytest.fixture
def openapi(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json()


def test_titulo_y_version_de_la_api(openapi):
    assert openapi["info"]["title"] == "API de Seguimiento de Hábitos de Bienestar"
    assert openapi["info"]["version"] == "1.0.0"


def test_documentacion_swagger_disponible(client):
    assert client.get("/docs").status_code == 200


@pytest.mark.parametrize("esquema", ESQUEMAS, ids=lambda e: e.__name__)
def test_esquema_tiene_ejemplo_en_openapi(openapi, esquema):
    componente = openapi["components"]["schemas"][esquema.__name__]
    assert componente.get("examples"), f"{esquema.__name__} no tiene ejemplos"


@pytest.mark.parametrize("esquema", ESQUEMAS, ids=lambda e: e.__name__)
def test_ejemplos_son_validos_para_su_esquema(esquema):
    for ejemplo in esquema.model_config["json_schema_extra"]["examples"]:
        esquema.model_validate(ejemplo)


def test_todos_los_errores_documentados_tienen_ejemplo(openapi):
    total = 0
    for ruta, operaciones in openapi["paths"].items():
        for metodo, operacion in operaciones.items():
            for codigo, respuesta in operacion["responses"].items():
                if codigo in ("400", "404", "409", "422"):
                    total += 1
                    contenido = respuesta["content"]["application/json"]
                    assert "error" in contenido["example"], f"{metodo} {ruta} {codigo}"
    assert total > 0


def test_ejemplo_de_creacion_funciona_contra_la_api(client):
    ejemplo = UsuarioCreate.model_config["json_schema_extra"]["examples"][0]
    assert client.post("/usuarios/", json=ejemplo).status_code == 201
