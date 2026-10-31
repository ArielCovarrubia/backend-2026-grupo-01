from tests.conftest import assert_error


def test_crear_categoria(client):
    r = client.post("/categorias/", json={"nombre": "  Sueño  ", "descripcion": "Dormir bien"})
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["id"] == 1
    assert cuerpo["nombre"] == "Sueño"
    assert cuerpo["descripcion"] == "Dormir bien"
    assert cuerpo["activa"] is True
    assert "orden_prioridad" in cuerpo


def test_listar_categorias(client, categoria):
    r = client.get("/categorias/")
    assert r.status_code == 200
    assert r.json() == [categoria]


def test_obtener_categoria(client, categoria):
    r = client.get(f"/categorias/{categoria['id']}")
    assert r.status_code == 200
    assert r.json() == categoria


def test_actualizar_categoria(client, categoria):
    r = client.put(f"/categorias/{categoria['id']}", json={"nombre": "Deporte", "descripcion": "Nueva"})
    assert r.status_code == 200
    assert r.json()["nombre"] == "Deporte"
    assert r.json()["descripcion"] == "Nueva"


def test_desactivar_y_activar_categoria(client, categoria):
    r = client.put(f"/categorias/{categoria['id']}", json={"activa": False})
    assert r.json()["activa"] is False
    r = client.put(f"/categorias/{categoria['id']}", json={"activa": True})
    assert r.json()["activa"] is True


def test_actualizar_categoria_mismo_nombre_propio(client, categoria):
    r = client.put(f"/categorias/{categoria['id']}", json={"nombre": categoria["nombre"]})
    assert r.status_code == 200


def test_eliminar_categoria(client, categoria):
    assert client.delete(f"/categorias/{categoria['id']}").status_code == 204
    assert_error(client.get(f"/categorias/{categoria['id']}"), 404, "RESOURCE_NOT_FOUND")


def test_crear_categoria_duplicada_ignora_mayusculas(client, categoria):
    r = client.post("/categorias/", json={"nombre": categoria["nombre"].upper(), "descripcion": "x"})
    assert_error(r, 409, "CONFLICT")


def test_actualizar_categoria_nombre_de_otra(client, categoria):
    otra = client.post("/categorias/", json={"nombre": "Sueño", "descripcion": "x"}).json()
    r = client.put(f"/categorias/{otra['id']}", json={"nombre": categoria["nombre"]})
    assert_error(r, 409, "CONFLICT")


def test_eliminar_categoria_con_habitos_asociados(client, habito, categoria):
    r = client.delete(f"/categorias/{categoria['id']}")

    assert_error(r, 400, "BUSINESS_RULE_ERROR")
    assert client.get(f"/categorias/{categoria['id']}").status_code == 200


def test_obtener_categoria_inexistente(client):
    assert_error(client.get("/categorias/999"), 404, "RESOURCE_NOT_FOUND")


def test_actualizar_categoria_inexistente(client):
    assert_error(client.put("/categorias/999", json={"nombre": "Algo"}), 404, "RESOURCE_NOT_FOUND")


def test_eliminar_categoria_inexistente(client):
    assert_error(client.delete("/categorias/999"), 404, "RESOURCE_NOT_FOUND")


def test_crear_categoria_nombre_solo_espacios(client):
    assert_error(client.post("/categorias/", json={"nombre": "    ", "descripcion": "x"}), 422, "VALIDATION_ERROR")


def test_crear_categoria_nombre_corto(client):
    assert_error(client.post("/categorias/", json={"nombre": "ab", "descripcion": "x"}), 422, "VALIDATION_ERROR")


def test_crear_categoria_descripcion_muy_larga(client):
    r = client.post("/categorias/", json={"nombre": "Valida", "descripcion": "x" * 201})
    assert_error(r, 422, "VALIDATION_ERROR")


def test_crear_categoria_sin_descripcion(client):
    assert_error(client.post("/categorias/", json={"nombre": "Valida"}), 422, "VALIDATION_ERROR")


def test_actualizar_categoria_activa_invalida(client, categoria):
    r = client.put(f"/categorias/{categoria['id']}", json={"activa": "quizas"})
    assert_error(r, 422, "VALIDATION_ERROR")
