import pytest

from app.application.services import health_service
from tests.conftest import assert_error


@pytest.mark.api
def test_health_reports_api_and_database_ok(client_sin_login):
    response = client_sin_login.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.api
def test_health_returns_503_when_database_is_down(client_sin_login, monkeypatch):
    monkeypatch.setattr(health_service, "check_database", lambda db: False)

    response = client_sin_login.get("/health")

    assert_error(response, 503, "HTTP_ERROR")