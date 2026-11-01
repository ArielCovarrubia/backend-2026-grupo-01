import pytest

from tests.conftest import assert_error


def _crear(client, usuario_id, categoria_id, nombre, frecuencia=3):
    r = client.post(
        "/habitos/",
        json={"usuario_id": usuario_id, "categoria_id": categoria_id, "nombre": nombre, "frecuencia_semanal": frecuencia},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_crear_habito(client, usuario, categoria):
    r = client.post(
        "/habitos/",
        json={"usuario_id": usuario["id"], "categoria_id": categoria["id"], "nombre": "  Correr  ", "frecuencia_semanal": 4},
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["id"] == 1
    assert cuerpo["nombre"] == "Correr"
    assert cuerpo["estado"] == "ACTIVO"
    assert cuerpo["frecuencia_semanal"] == 4
    assert "fecha_creacion" in cuerpo


def test_obtener_habito(client, habito):
    r = client.get(f"/habitos/{habito['id']}")
    assert r.status_code == 200
    assert r.json() == habito


def test_actualizar_habito(client, habito):
    r = client.put(f"/habitos/{habito['id']}", json={"nombre": "Trotar", "frecuencia_semanal": 5, "estado": "PAUSADO"})
    assert r.status_code == 200
    assert (r.json()["nombre"], r.json()["frecuencia_semanal"], r.json()["estado"]) == ("Trotar", 5, "PAUSADO")


def test_actualizar_habito_cambia_categoria(client, habito):
    nueva = client.post("/categorias/", json={"nombre": "Sueño", "descripcion": "x"}).json()
    r = client.put(f"/habitos/{habito['id']}", json={"categoria_id": nueva["id"]})
    assert r.status_code == 200
    assert r.json()["categoria_id"] == nueva["id"]


def test_eliminar_habito_lo_archiva(client, habito):
    assert client.delete(f"/habitos/{habito['id']}").status_code == 204
    r = client.get(f"/habitos/{habito['id']}")
    assert r.status_code == 200
    assert r.json()["estado"] == "ARCHIVADO"


def test_crear_habito_usuario_inexistente(client, categoria):
    r = client.post("/habitos/", json={"usuario_id": 99, "categoria_id": categoria["id"], "nombre": "Correr", "frecuencia_semanal": 3})
    assert_error(r, 404, "RESOURCE_NOT_FOUND")


def test_crear_habito_categoria_inexistente(client, usuario):
    r = client.post("/habitos/", json={"usuario_id": usuario["id"], "categoria_id": 99, "nombre": "Correr", "frecuencia_semanal": 3})
    assert_error(r, 404, "RESOURCE_NOT_FOUND")


def test_crear_habito_duplicado_mismo_usuario(client, habito):
    r = client.post(
        "/habitos/",
        json={"usuario_id": habito["usuario_id"], "categoria_id": habito["categoria_id"], "nombre": "CORRER", "frecuencia_semanal": 2},
    )
    assert_error(r, 409, "CONFLICT")


def test_mismo_nombre_en_otro_usuario_es_valido(client, habito):
    otro = client.post("/usuarios/", json={"name": "Otro", "email": "otro@alu.uct.cl"}).json()
    _crear(client, otro["id"], habito["categoria_id"], "Correr")


def test_actualizar_habito_nombre_duplicado(client, habito):
    otro = _crear(client, habito["usuario_id"], habito["categoria_id"], "Nadar")
    r = client.put(f"/habitos/{otro['id']}", json={"nombre": "correr"})
    assert_error(r, 409, "CONFLICT")


def test_actualizar_habito_categoria_inexistente(client, habito):
    assert_error(client.put(f"/habitos/{habito['id']}", json={"categoria_id": 99}), 404, "RESOURCE_NOT_FOUND")


@pytest.mark.parametrize("metodo", ["get", "delete"])
def test_habito_inexistente_get_delete(client, metodo):
    assert_error(getattr(client, metodo)("/habitos/999"), 404, "RESOURCE_NOT_FOUND")


def test_actualizar_habito_inexistente(client):
    assert_error(client.put("/habitos/999", json={"nombre": "Algo"}), 404, "RESOURCE_NOT_FOUND")


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "ab"},
        {"nombre": "   "},
        {"nombre": "x" * 51},
        {"frecuencia_semanal": 0},
        {"frecuencia_semanal": 8},
        {"frecuencia_semanal": "mucho"},
    ],
)
def test_crear_habito_datos_invalidos(client, usuario, categoria, cambios):
    cuerpo = {"usuario_id": usuario["id"], "categoria_id": categoria["id"], "nombre": "Correr", "frecuencia_semanal": 3, **cambios}
    assert_error(client.post("/habitos/", json=cuerpo), 422, "VALIDATION_ERROR")


def test_actualizar_habito_estado_invalido(client, habito):
    assert_error(client.put(f"/habitos/{habito['id']}", json={"estado": "ROTO"}), 422, "VALIDATION_ERROR")


@pytest.fixture
def varios(client, usuario, categoria):
    sueno = client.post("/categorias/", json={"nombre": "Sueño", "descripcion": "x"}).json()
    otro = client.post("/usuarios/", json={"name": "Otro", "email": "otro@alu.uct.cl"}).json()
    return {
        "usuario": usuario,
        "otro": otro,
        "categoria": categoria,
        "sueno": sueno,
        "habitos": [
            _crear(client, usuario["id"], categoria["id"], "Correr", 5),
            _crear(client, usuario["id"], sueno["id"], "Dormir temprano", 7),
            _crear(client, usuario["id"], categoria["id"], "Abdominales", 2),
            _crear(client, otro["id"], categoria["id"], "Yoga", 1),
        ],
    }


def _nombres(r):
    assert r.status_code == 200, r.text
    return [h["nombre"] for h in r.json()["items"]]


def test_listar_habitos_orden_por_defecto_es_nombre(client, varios):
    assert _nombres(client.get("/habitos/")) == ["Abdominales", "Correr", "Dormir temprano", "Yoga"]


def test_filtrar_por_usuario(client, varios):
    r = client.get("/habitos/", params={"usuario_id": varios["otro"]["id"]})
    assert _nombres(r) == ["Yoga"]


def test_filtrar_por_categoria(client, varios):
    r = client.get("/habitos/", params={"categoria_id": varios["sueno"]["id"]})
    assert _nombres(r) == ["Dormir temprano"]


def test_filtrar_por_estado_ignora_mayusculas(client, varios):
    client.delete(f"/habitos/{varios['habitos'][0]['id']}")
    assert _nombres(client.get("/habitos/", params={"estado": "archivado"})) == ["Correr"]
    assert "Correr" not in _nombres(client.get("/habitos/", params={"estado": "ACTIVO"}))


def test_combinar_filtros(client, varios):
    r = client.get("/habitos/", params={"usuario_id": varios["usuario"]["id"], "categoria_id": varios["categoria"]["id"]})
    assert _nombres(r) == ["Abdominales", "Correr"]


def test_ordenar_por_frecuencia_semanal(client, varios):
    assert _nombres(client.get("/habitos/", params={"orden": "frecuencia_semanal"})) == [
        "Yoga", "Abdominales", "Correr", "Dormir temprano",
    ]


def test_ordenar_por_fecha_creacion(client, varios):
    assert _nombres(client.get("/habitos/", params={"orden": "fecha_creacion"})) == [
        "Correr", "Dormir temprano", "Abdominales", "Yoga",
    ]


def test_paginacion(client, varios):
    p1 = _nombres(client.get("/habitos/", params={"pagina": 1, "tamano_pagina": 3}))
    p2 = _nombres(client.get("/habitos/", params={"pagina": 2, "tamano_pagina": 3}))
    p3 = _nombres(client.get("/habitos/", params={"pagina": 3, "tamano_pagina": 3}))
    assert p1 == ["Abdominales", "Correr", "Dormir temprano"]
    assert p2 == ["Yoga"]
    assert p3 == []


def test_paginacion_incluye_metadatos(client, varios):
    r = client.get("/habitos/", params={"pagina": 2, "tamano_pagina": 3})
    cuerpo = r.json()
    assert cuerpo["total"] == 4
    assert cuerpo["pagina"] == 2
    assert cuerpo["limite"] == 3
    assert cuerpo["total_paginas"] == 2
    assert len(cuerpo["items"]) == 1


def test_paginacion_sin_resultados_tiene_una_pagina(client):
    cuerpo = client.get("/habitos/").json()
    assert cuerpo == {"items": [], "total": 0, "pagina": 1, "limite": 10, "total_paginas": 1}


def test_ordenar_por_y_direccion_descendente(client, varios):
    r = client.get("/habitos/", params={"ordenar_por": "frecuencia_semanal", "direccion": "desc"})
    assert _nombres(r) == ["Dormir temprano", "Correr", "Abdominales", "Yoga"]


def test_limite_define_el_tamano_de_pagina(client, varios):
    cuerpo = client.get("/habitos/", params={"limite": 2}).json()
    assert cuerpo["limite"] == 2
    assert cuerpo["total_paginas"] == 2
    assert len(cuerpo["items"]) == 2


@pytest.mark.parametrize("params", [{"limite": 0}, {"limite": 101}, {"direccion": "arriba"}])
def test_parametros_de_listado_fuera_de_rango(client, params):
    assert_error(client.get("/habitos/", params=params), 400, "BUSINESS_RULE_ERROR")


def test_orden_invalido(client, varios):
    assert_error(client.get("/habitos/", params={"orden": "color"}), 400, "BUSINESS_RULE_ERROR")


@pytest.mark.parametrize("params", [{"pagina": 0}, {"tamano_pagina": 0}, {"pagina": -1}])
def test_paginacion_invalida(client, params):
    assert_error(client.get("/habitos/", params=params), 400, "BUSINESS_RULE_ERROR")


def test_paginacion_no_numerica(client):
    assert_error(client.get("/habitos/", params={"pagina": "x"}), 422, "VALIDATION_ERROR")
