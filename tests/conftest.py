import os
import tempfile
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

_directorio_temporal = tempfile.mkdtemp(prefix="habitos_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{_directorio_temporal}/test.db"

from app.infrastructure.database import Base, engine
from app.infrastructure.repositories import (
    categoria_repository,
    habito_repository,
    registro_repository,
    usuario_repository,
)
from app.main import app

ALMACENES_EN_MEMORIA = {
    usuario_repository: "_usuarios",
    categoria_repository: "_categorias",
    habito_repository: "_habitos",
    registro_repository: "_registros",
}


def _limpiar_almacenes_en_memoria() -> None:
    for repo, nombre in ALMACENES_EN_MEMORIA.items():
        if hasattr(repo, nombre):
            getattr(repo, nombre).clear()
            repo._contador_id = 0


@pytest.fixture(autouse=True)
def base_de_datos_limpia():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    _limpiar_almacenes_en_memoria()
    yield
    _limpiar_almacenes_en_memoria()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def usuario(client):
    r = client.post("/usuarios/", json={"name": "Patricio", "email": "pato@alu.uct.cl"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def categoria(client):
    r = client.post("/categorias/", json={"nombre": "Ejercicio", "descripcion": "Actividad física"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def habito(client, usuario, categoria):
    r = client.post(
        "/habitos/",
        json={
            "usuario_id": usuario["id"],
            "categoria_id": categoria["id"],
            "nombre": "Correr",
            "frecuencia_semanal": 3,
        },
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def registro(client, habito):
    r = client.post(
        "/registros/",
        json={"habito_id": habito["id"], "fecha_registro": date.today().isoformat()},
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def ayer() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


@pytest.fixture
def manana() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def assert_error(response, status: int, code: str) -> dict:
    assert response.status_code == status, response.text
    cuerpo = response.json()
    assert set(cuerpo) == {"error"}
    assert cuerpo["error"]["code"] == code
    assert isinstance(cuerpo["error"]["message"], str) and cuerpo["error"]["message"]
    assert isinstance(cuerpo["error"]["details"], list)
    return cuerpo["error"]
