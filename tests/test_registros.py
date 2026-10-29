import pytest

from tests.conftest import assert_error


def _body(habito_id, fecha, **extra):
    return {"habito_id": habito_id, "fecha_registro": fecha, **extra}


def test_crear_registro(client, habito, ayer):
    r = client.post("/registros/", json=_body(habito["id"], ayer, valor_medido=30.5, nota="30 min"))
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["id"] == 1
    assert cuerpo["completado"] is True
    assert cuerpo["valor_medido"] == 30.5
    assert cuerpo["nota"] == "30 min"
    assert cuerpo["fecha_registro"] == ayer
    assert "creado_en" in cuerpo


def test_crear_registro_hoy_es_valido(client, habito):
    from datetime import date

    r = client.post("/registros/", json=_body(habito["id"], date.today().isoformat()))
    assert r.status_code == 201


def test_listar_registros(client, registro):
    r = client.get("/registros/")
    assert r.status_code == 200
    assert [x["id"] for x in r.json()] == [registro["id"]]


def test_obtener_registro(client, registro):
    r = client.get(f"/registros/{registro['id']}")
    assert r.status_code == 200
    assert r.json() == registro


def test_actualizar_registro(client, registro):
    r = client.put(f"/registros/{registro['id']}", json={"completado": False, "valor_medido": 10, "nota": "cansado"})
    assert r.status_code == 200
    assert (r.json()["completado"], r.json()["valor_medido"], r.json()["nota"]) == (False, 10, "cansado")
    assert r.json()["fecha_registro"] == registro["fecha_registro"]


def test_eliminar_registro(client, registro):
    assert client.delete(f"/registros/{registro['id']}").status_code == 204
    assert_error(client.get(f"/registros/{registro['id']}"), 404, "RESOURCE_NOT_FOUND")


def test_registro_fecha_futura(client, habito, manana):
    r = client.post("/registros/", json=_body(habito["id"], manana))
    assert_error(r, 400, "BUSINESS_RULE_ERROR")


def test_registro_duplicado_misma_fecha(client, habito, ayer):
    assert client.post("/registros/", json=_body(habito["id"], ayer)).status_code == 201
    assert_error(client.post("/registros/", json=_body(habito["id"], ayer)), 409, "CONFLICT")


def test_misma_fecha_en_otro_habito_es_valida(client, habito, ayer):
    otro = client.post(
        "/habitos/",
        json={"usuario_id": habito["usuario_id"], "categoria_id": habito["categoria_id"], "nombre": "Nadar", "frecuencia_semanal": 2},
    ).json()
    assert client.post("/registros/", json=_body(habito["id"], ayer)).status_code == 201
    assert client.post("/registros/", json=_body(otro["id"], ayer)).status_code == 201


def test_registro_habito_inexistente(client, ayer):
    assert_error(client.post("/registros/", json=_body(999, ayer)), 404, "RESOURCE_NOT_FOUND")


@pytest.mark.parametrize("metodo", ["get", "delete"])
def test_registro_inexistente_get_delete(client, metodo):
    assert_error(getattr(client, metodo)("/registros/999"), 404, "RESOURCE_NOT_FOUND")


def test_actualizar_registro_inexistente(client):
    assert_error(client.put("/registros/999", json={"completado": False}), 404, "RESOURCE_NOT_FOUND")


@pytest.mark.parametrize(
    "extra",
    [
        {"valor_medido": -1},
        {"nota": "x" * 201},
        {"completado": "tal vez"},
        {"fecha_registro": "ayer"},
        {"fecha_registro": "2026-13-45"},
    ],
)
def test_crear_registro_datos_invalidos(client, habito, ayer, extra):
    cuerpo = {**_body(habito["id"], ayer), **extra}
    assert_error(client.post("/registros/", json=cuerpo), 422, "VALIDATION_ERROR")


def test_crear_registro_sin_campos_obligatorios(client):
    error = assert_error(client.post("/registros/", json={}), 422, "VALIDATION_ERROR")
    assert {"habito_id", "fecha_registro"} <= {d["field"] for d in error["details"]}


def test_actualizar_registro_valor_negativo(client, registro):
    assert_error(client.put(f"/registros/{registro['id']}", json={"valor_medido": -5}), 422, "VALIDATION_ERROR")
