import pytest


@pytest.mark.xfail(strict=True, reason="Bug 6: el email se compara sensible a mayúsculas")
def test_email_duplicado_ignora_mayusculas(client):
    client.post("/usuarios/", json={"name": "Ana", "email": "Ana@x.cl"})
    r = client.post("/usuarios/", json={"name": "Ana Dos", "email": "ana@x.cl"})
    assert r.status_code == 409


@pytest.mark.xfail(strict=True, reason="Bug 7: eliminar usuario deja hábitos huérfanos")
def test_eliminar_usuario_con_habitos_no_deja_huerfanos(client, habito):
    r = client.delete(f"/usuarios/{habito['usuario_id']}")
    assert r.status_code in (400, 409)


@pytest.mark.xfail(strict=True, reason="Bug 8: se puede crear un hábito en una categoría inactiva")
def test_no_crear_habito_en_categoria_inactiva(client, usuario, categoria):
    client.put(f"/categorias/{categoria['id']}", json={"activa": False})
    r = client.post(
        "/habitos/",
        json={"usuario_id": usuario["id"], "categoria_id": categoria["id"], "nombre": "Correr", "frecuencia_semanal": 3},
    )
    assert r.status_code >= 400


@pytest.mark.xfail(strict=True, reason="Bug 9: se pueden crear registros sobre un hábito archivado")
def test_no_crear_registro_en_habito_archivado(client, habito, ayer):
    client.delete(f"/habitos/{habito['id']}")
    r = client.post("/registros/", json={"habito_id": habito["id"], "fecha_registro": ayer})
    assert r.status_code >= 400


@pytest.mark.xfail(strict=True, reason="Bug 10: filtro estado inválido devuelve 200 en vez de error")
def test_filtro_estado_invalido_es_error(client):
    assert client.get("/habitos/", params={"estado": "xyz"}).status_code in (400, 422)


@pytest.mark.xfail(strict=True, reason="Bug 11: nota compuesta solo por espacios se acepta")
def test_nota_solo_espacios_se_rechaza(client, habito, ayer):
    r = client.post("/registros/", json={"habito_id": habito["id"], "fecha_registro": ayer, "nota": "     "})
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason="Bug 12: el error no usa {'detail': {'code','message'}} como pide la guía")
def test_formato_error_segun_guia(client):
    cuerpo = client.get("/usuarios/999").json()
    assert "detail" in cuerpo and {"code", "message"} <= set(cuerpo["detail"])
