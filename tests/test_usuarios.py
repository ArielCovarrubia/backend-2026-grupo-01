from tests.conftest import assert_error


def test_crear_usuario(client):
    r = client.post("/usuarios/", json={"name": "  Ana  ", "email": "ana@correo.cl"})
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["id"] == 1
    assert cuerpo["name"] == "Ana"
    assert cuerpo["email"] == "ana@correo.cl"
    assert "fecha_registro" in cuerpo


def test_listar_usuarios(client, usuario):
    r = client.get("/usuarios/")
    assert r.status_code == 200
    assert [u["id"] for u in r.json()] == [usuario["id"]]


def test_listar_usuarios_vacio(client):
    assert client.get("/usuarios/").json() == []


def test_obtener_usuario(client, usuario):
    r = client.get(f"/usuarios/{usuario['id']}")
    assert r.status_code == 200
    assert r.json() == usuario


def test_actualizar_usuario(client, usuario):
    r = client.put(f"/usuarios/{usuario['id']}", json={"name": "Pato", "email": "nuevo@alu.uct.cl"})
    assert r.status_code == 200
    assert r.json()["name"] == "Pato"
    assert r.json()["email"] == "nuevo@alu.uct.cl"
    assert r.json()["fecha_registro"] == usuario["fecha_registro"]


def test_actualizar_usuario_parcial(client, usuario):
    r = client.put(f"/usuarios/{usuario['id']}", json={"name": "Solo Nombre"})
    assert r.status_code == 200
    assert r.json()["email"] == usuario["email"]


def test_actualizar_usuario_mismo_email_propio_no_es_conflicto(client, usuario):
    r = client.put(f"/usuarios/{usuario['id']}", json={"email": usuario["email"]})
    assert r.status_code == 200


def test_eliminar_usuario(client, usuario):
    assert client.delete(f"/usuarios/{usuario['id']}").status_code == 204
    assert_error(client.get(f"/usuarios/{usuario['id']}"), 404, "RESOURCE_NOT_FOUND")


def test_crear_usuario_email_duplicado(client, usuario):
    r = client.post("/usuarios/", json={"name": "Otro", "email": usuario["email"]})
    assert_error(r, 409, "CONFLICT")


def test_actualizar_usuario_email_de_otro(client, usuario):
    otro = client.post("/usuarios/", json={"name": "Otro", "email": "otro@alu.uct.cl"}).json()
    r = client.put(f"/usuarios/{otro['id']}", json={"email": usuario["email"]})
    assert_error(r, 409, "CONFLICT")


def test_obtener_usuario_inexistente(client):
    assert_error(client.get("/usuarios/999"), 404, "RESOURCE_NOT_FOUND")


def test_actualizar_usuario_inexistente(client):
    assert_error(client.put("/usuarios/999", json={"name": "Ana"}), 404, "RESOURCE_NOT_FOUND")


def test_eliminar_usuario_inexistente(client):
    assert_error(client.delete("/usuarios/999"), 404, "RESOURCE_NOT_FOUND")


def test_crear_usuario_email_invalido(client):
    error = assert_error(client.post("/usuarios/", json={"name": "Ana", "email": "no-es-email"}), 422, "VALIDATION_ERROR")
    assert any(d["field"] == "email" for d in error["details"])


def test_crear_usuario_nombre_solo_espacios(client):
    r = client.post("/usuarios/", json={"name": "     ", "email": "ana@correo.cl"})
    assert_error(r, 422, "VALIDATION_ERROR")


def test_crear_usuario_nombre_muy_corto(client):
    assert_error(client.post("/usuarios/", json={"name": "A", "email": "a@correo.cl"}), 422, "VALIDATION_ERROR")


def test_crear_usuario_nombre_muy_largo(client):
    r = client.post("/usuarios/", json={"name": "x" * 61, "email": "a@correo.cl"})
    assert_error(r, 422, "VALIDATION_ERROR")


def test_crear_usuario_sin_campos(client):
    error = assert_error(client.post("/usuarios/", json={}), 422, "VALIDATION_ERROR")
    campos = {d["field"] for d in error["details"]}
    assert {"name", "email"} <= campos


def test_id_no_numerico(client):
    assert_error(client.get("/usuarios/abc"), 422, "VALIDATION_ERROR")
