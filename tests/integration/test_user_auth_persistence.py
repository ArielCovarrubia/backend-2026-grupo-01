from datetime import UTC, datetime

import pytest


@pytest.mark.integration
def test_persisted_user_stores_only_argon2id_password_hash(session, user):
    from app.infrastructure.models.usuario_model import UsuarioModel

    stored = session.query(UsuarioModel).filter_by(id=user.id).one()
    assert stored.password_hash.startswith("$argon2id$")
    assert "example-password-123" not in repr(stored.__dict__)


@pytest.mark.integration
@pytest.mark.xfail(reason="Refresh token family identifiers are pending in the model.")
def test_refresh_rotation_revokes_old_token_and_preserves_family(session, user):
    from app.application.services.auth_service import (
        create_refresh_token,
        rotate_refresh_token,
    )
    from app.infrastructure.models.refresh_token_model import RefreshTokenModel

    old_token = create_refresh_token(user.id, session)
    new_token, _ = rotate_refresh_token(old_token, session)
    records = session.query(RefreshTokenModel).order_by(RefreshTokenModel.id).all()

    assert records[0].revocado_en is not None
    assert records[0].familia_id == records[1].familia_id
    assert records[1].token_hash
    assert new_token != old_token


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Refresh-token reuse does not revoke the active token family yet."
)
def test_reusing_revoked_refresh_token_revokes_entire_family(session, user):
    from app.application.services.auth_service import (
        create_refresh_token,
        rotate_refresh_token,
    )
    from app.infrastructure.models.refresh_token_model import RefreshTokenModel

    old_token = create_refresh_token(user.id, session)
    rotate_refresh_token(old_token, session)
    assert rotate_refresh_token(old_token, session) is None

    records = session.query(RefreshTokenModel).filter_by(usuario_id=user.id).all()
    assert all(record.revocado_en is not None for record in records)
    assert all(
        record.revocado_en < datetime.now(UTC).replace(tzinfo=None)
        for record in records
    )
