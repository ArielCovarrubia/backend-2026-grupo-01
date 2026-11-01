import os
import socket
import subprocess
import sys
import time

import httpx
import pytest


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _levantar(url_bd: str, puerto: int) -> subprocess.Popen:
    entorno = {**os.environ, "DATABASE_URL": url_bd}
    proceso = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(puerto), "--log-level", "warning"],
        env=entorno,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        try:
            httpx.get(f"http://127.0.0.1:{puerto}/usuarios/", timeout=1)
            return proceso
        except httpx.HTTPError:
            time.sleep(0.1)
    proceso.terminate()
    pytest.fail("El servidor no levantó a tiempo")


def _detener(proceso: subprocess.Popen) -> None:
    proceso.terminate()
    proceso.wait(timeout=10)


def test_datos_persisten_tras_reiniciar_el_servidor(tmp_path):
    url_bd = f"sqlite:///{tmp_path}/persistencia.db"
    puerto = _puerto_libre()
    base = f"http://127.0.0.1:{puerto}"

    servidor = _levantar(url_bd, puerto)
    try:
        r = httpx.post(f"{base}/usuarios/", json={"name": "Persistente", "email": "persist@x.cl"})
        assert r.status_code == 201
        usuario_id = r.json()["id"]
    finally:
        _detener(servidor)

    servidor = _levantar(url_bd, puerto)
    try:
        r = httpx.get(f"{base}/usuarios/{usuario_id}")
        assert r.status_code == 200
        assert r.json()["email"] == "persist@x.cl"
    finally:
        _detener(servidor)
