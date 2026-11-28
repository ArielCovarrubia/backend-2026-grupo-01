import pytest

from app.application.services.auth_service import create_access_token


@pytest.mark.api
def test_auth_me_and_owner_permissions(client_sin_login, create_user):
    owner = create_user(email="owner@x.cl")
    other = create_user(email="other@x.cl")

    owner_headers = {"Authorization": f"Bearer {create_access_token(owner.id, owner.token_version)}"}
    other_headers = {"Authorization": f"Bearer {create_access_token(other.id, other.token_version)}"}

    me = client_sin_login.get("/auth/me", headers=owner_headers)
    assert me.status_code == 200
    assert me.json()["id"] == owner.id

    other_usuario = client_sin_login.get(f"/usuarios/{owner.id}", headers=other_headers)
    assert other_usuario.status_code == 403

    own_usuario = client_sin_login.get(f"/usuarios/{owner.id}", headers=owner_headers)
    assert own_usuario.status_code == 200

    listed = client_sin_login.get("/usuarios/", headers=other_headers)
    assert listed.status_code == 403


@pytest.mark.api
def test_forgot_password_never_discloses_or_returns_token(client_sin_login, create_user):
    create_user(email="known@x.cl")

    known = client_sin_login.post("/auth/forgot-password", json={"email": "known@x.cl"})
    unknown = client_sin_login.post("/auth/forgot-password", json={"email": "unknown@x.cl"})

    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json() == unknown.json()
    assert "token" not in known.json()


@pytest.mark.api
def test_password_recovery_sends_mail_and_limits_requests(
    client_sin_login,
    create_user,
    monkeypatch,
):
    create_user(email="mail@x.cl")
    sent = []

    def fake_send(email, token):
        sent.append((email, token))

    monkeypatch.setattr(
        "app.presentation.routers.auth.send_password_reset_email",
        fake_send,
    )

    for _ in range(5):
        response = client_sin_login.post(
            "/auth/forgot-password",
            json={"email": "mail@x.cl"},
        )
        assert response.status_code == 200

    before = len(sent)
    sixth = client_sin_login.post(
        "/auth/forgot-password",
        json={"email": "mail@x.cl"},
    )
    assert sixth.status_code == 200
    assert len(sent) == before
