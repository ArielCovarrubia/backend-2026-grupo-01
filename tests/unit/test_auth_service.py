from unittest.mock import Mock

import pytest

from app.domain.usuario import Usuario


@pytest.mark.xfail(reason="Usuario login lockout state is pending in the domain model.")
def test_fifth_failed_login_locks_account():
    user = Usuario(id=1, name="Ana", email="ana@example.test")
    for _ in range(5):
        user.registrar_fallo()
    assert user.esta_bloqueado()


@pytest.mark.xfail(reason="Usuario login lockout state is pending in the domain model.")
def test_fewer_than_five_failed_logins_leave_account_unlocked():
    user = Usuario(id=1, name="Ana", email="ana@example.test")
    for _ in range(4):
        user.registrar_fallo()
    assert not user.esta_bloqueado()


@pytest.mark.parametrize(
    "scenario",
    ["success", "wrong_password", "locked_account", "unknown_email"],
)
@pytest.mark.xfail(
    reason="Repository-injected AuthService is pending in the application layer."
)
def test_auth_service_handles_login_scenario(scenario):
    from app.application.services.auth_service import AuthService

    users = Mock()
    passwords = Mock()
    service = AuthService(usuario_repository=users, password_hasher=passwords)
    service.login("ana@example.test", "example-password-123", scenario=scenario)


@pytest.mark.parametrize("state", ["valid", "expired", "revoked"])
@pytest.mark.xfail(reason="RefreshToken domain entity and esta_vigente are pending.")
def test_refresh_token_vigencia_matches_state(state):
    from app.domain.refresh_token import RefreshToken

    token = RefreshToken.from_state(state)
    assert token.esta_vigente() is (state == "valid")


def test_revoke_all_sessions_marks_user_refresh_tokens_revoked(session, user):
    from app.application.services.auth_service import (
        create_refresh_token,
        revoke_all_sessions,
    )
    from app.infrastructure.models.refresh_token_model import RefreshTokenModel

    create_refresh_token(user.id, session)
    revoke_all_sessions(user.id, session)

    tokens = session.query(RefreshTokenModel).filter_by(usuario_id=user.id).all()
    assert len(tokens) == 1
    assert tokens[0].revocado_en is not None
