import importlib
from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.domain.exceptions import TokenInvalido


@pytest.mark.xfail(reason="RegistroDTO with the required password policy is pending.")
def test_registration_dto_rejects_short_password():
    schema = importlib.import_module("app.presentation.schemas.auth_schema")
    registration_dto = vars(schema)["RegistroDTO"]
    with pytest.raises(ValidationError):
        registration_dto(name="Ana Example", email="ana@example.test", password="short")


@pytest.mark.xfail(reason="RegistroDTO with forbidden extra fields is pending.")
def test_registration_dto_forbids_extra_fields():
    schema = importlib.import_module("app.presentation.schemas.auth_schema")
    registration_dto = vars(schema)["RegistroDTO"]
    with pytest.raises(ValidationError):
        registration_dto(
            name="Ana Example",
            email="ana@example.test",
            password="example-password-123",
            extra="unexpected",
        )


def test_argon2id_hashes_use_distinct_salts_and_verify_password():
    from app.application.services.auth_service import hash_password, verify_password

    password = "example-password-123"
    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert first_hash.startswith("$argon2id$")
    assert second_hash.startswith("$argon2id$")
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_tampered_jwt_signature_raises_token_invalido():
    from app.application.services.auth_service import (
        create_access_token,
        decode_token,
    )

    header, payload, signature = create_access_token(1).split(".")
    first = "A" if signature[0] != "A" else "B"
    tampered = f"{header}.{payload}.{first}{signature[1:]}"
    with pytest.raises(TokenInvalido):
        decode_token(tampered, "access")


def test_expired_token_raises_token_invalido():
    from app.infrastructure.security.tokens import decode_token, encode_token

    expired = encode_token(1, "access", timedelta(seconds=-1))
    with pytest.raises(TokenInvalido):
        decode_token(expired, "access")


def test_access_token_is_rejected_as_reset_token():
    from app.application.services.auth_service import create_access_token, decode_token

    with pytest.raises(TokenInvalido):
        decode_token(create_access_token(1), "reset")