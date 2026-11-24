from datetime import datetime

import pytest

from app.domain.exceptions import ConflictoError
from app.presentation.schemas.usuario_schema import UsuarioCreate


@pytest.mark.integration
def test_case_insensitive_duplicate_email_is_rejected(session):
    from app.application.services.usuario_service import crear_usuario

    crear_usuario(UsuarioCreate(name="Ana One", email="ana@x.cl"), db=session)

    with pytest.raises(ConflictoError):
        crear_usuario(UsuarioCreate(name="Ana Two", email="ANA@X.CL"), db=session)


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Global logout and token_version are pending in the auth implementation."
)
def test_global_logout_increments_token_version_and_revokes_refresh_tokens(
    session, user
):
    from app.application.services.auth_service import (
        create_refresh_token,
        revoke_all_sessions,
    )
    from app.infrastructure.models.refresh_token_model import RefreshTokenModel
    from app.infrastructure.models.usuario_model import UsuarioModel

    create_refresh_token(user.id, session)
    create_refresh_token(user.id, session)
    revoke_all_sessions(user.id, session)

    stored_user = session.query(UsuarioModel).filter_by(id=user.id).one()
    tokens = session.query(RefreshTokenModel).filter_by(usuario_id=user.id).all()
    assert stored_user.token_version == 1
    assert all(token.revocado_en is not None for token in tokens)


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Account lockout persistence is pending in the domain and model."
)
def test_five_failed_logins_persist_future_lockout(session, user):
    from app.domain.usuario import Usuario
    from app.infrastructure.models.usuario_model import UsuarioModel

    domain_user = Usuario(id=user.id, name=user.name, email=user.email)
    for _ in range(5):
        domain_user.registrar_fallo()

    stored = session.query(UsuarioModel).filter_by(id=user.id).one()
    stored.bloqueado_hasta = domain_user.bloqueado_hasta
    session.commit()
    assert stored.bloqueado_hasta is not None
    assert stored.bloqueado_hasta > datetime.now()
