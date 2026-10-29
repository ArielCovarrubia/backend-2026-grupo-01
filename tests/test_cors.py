ORIGEN_PERMITIDO = "http://localhost:5173"


def _preflight(client, origen, metodo="POST", headers="content-type"):
    return client.options(
        "/usuarios/",
        headers={
            "Origin": origen,
            "Access-Control-Request-Method": metodo,
            "Access-Control-Request-Headers": headers,
        },
    )


def test_preflight_origen_permitido(client):
    r = _preflight(client, ORIGEN_PERMITIDO, headers="content-type, authorization")
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO
    permitidos = r.headers["access-control-allow-methods"]
    for metodo in ("GET", "POST", "PUT", "DELETE"):
        assert metodo in permitidos
    cabeceras = r.headers["access-control-allow-headers"].lower()
    assert "content-type" in cabeceras and "authorization" in cabeceras


def test_preflight_origen_no_permitido(client):
    r = _preflight(client, "http://sitio-malicioso.com")
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


def test_preflight_metodo_no_permitido(client):
    r = _preflight(client, ORIGEN_PERMITIDO, metodo="PATCH")
    assert r.status_code == 400


def test_respuesta_normal_incluye_cabecera_cors(client):
    r = client.get("/usuarios/", headers={"Origin": ORIGEN_PERMITIDO})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO


def test_respuesta_de_error_tambien_incluye_cors(client):
    r = client.get("/usuarios/999", headers={"Origin": ORIGEN_PERMITIDO})
    assert r.status_code == 404
    assert r.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO


def test_origen_no_permitido_no_recibe_cabecera(client):
    r = client.get("/usuarios/", headers={"Origin": "http://sitio-malicioso.com"})
    assert "access-control-allow-origin" not in r.headers
