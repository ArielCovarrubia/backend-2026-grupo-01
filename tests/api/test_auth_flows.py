import pytest


@pytest.mark.api
def test_register_login_bearer_logout_and_reject_refresh(client_sin_login):
    registration = client_sin_login.post(
        "/usuarios/",
        json={
            "name": "Ana Example",
            "email": "e2e-access@example.test",
            "password": "example-password-123",
        },
    )
    assert registration.status_code == 201, registration.text

    login = client_sin_login.post(
        "/auth/login",
        json={"email": "e2e-access@example.test", "password": "example-password-123"},
    )
    assert login.status_code == 200, login.text
    access_token = login.json()["access_token"]

    response = client_sin_login.get(
        "/categorias/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    logout = client_sin_login.post("/auth/logout")
    assert logout.status_code == 204
    refresh = client_sin_login.post("/auth/refresh")
    assert refresh.status_code == 401


@pytest.mark.api
def test_password_recovery_is_single_use_and_updates_login(client_sin_login):
    client_sin_login.post(
        "/usuarios/",
        json={
            "name": "Ana Example",
            "email": "e2e-recovery@example.test",
            "password": "old-password-123",
        },
    )

    recovery = client_sin_login.post(
        "/auth/forgot-password", json={"email": "e2e-recovery@example.test"}
    )
    assert recovery.status_code == 200
    reset_token = recovery.json()["token"]
    reset_body = {"token": reset_token, "password": "new-password-123"}

    changed = client_sin_login.post("/auth/reset-password", json=reset_body)
    assert changed.status_code == 200
    reused = client_sin_login.post("/auth/reset-password", json=reset_body)
    assert reused.status_code == 400

    old_login = client_sin_login.post(
        "/auth/login",
        json={"email": "e2e-recovery@example.test", "password": "old-password-123"},
    )
    new_login = client_sin_login.post(
        "/auth/login",
        json={"email": "e2e-recovery@example.test", "password": "new-password-123"},
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200


@pytest.mark.api
def test_admin_category_route_requires_admin_access(client_sin_login, user, admin_user):
    from app.application.services.auth_service import create_access_token

    route = "/categorias/"
    body = {"nombre": "Admin category", "descripcion": "Created in API test"}
    assert client_sin_login.post(route, json=body).status_code == 401

    regular = client_sin_login.post(
        route,
        json=body,
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )
    assert regular.status_code == 403

    admin = client_sin_login.post(
        route,
        json=body,
        headers={"Authorization": f"Bearer {create_access_token(admin_user.id)}"},
    )
    assert admin.status_code == 201
