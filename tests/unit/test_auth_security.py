import importlib

import jwt
import pytest
from pydantic import ValidationError


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


@pytest.mark.xfail(
    reason="TokenInvalido is pending; current code raises PyJWT exceptions."
)
def test_tampered_jwt_signature_raises_token_invalido():
    service = importlib.import_module("app.application.services.auth_service")
    exceptions = importlib.import_module("app.domain.exceptions")
    token_invalido = vars(exceptions)["TokenInvalido"]
    token = service.create_access_token(1)
    header, payload, signature = token.split(".")
    tampered = f"{header}.{payload}.{signature[:-1]}x"
    with pytest.raises(token_invalido):
        service.decode_token(tampered, "access")


def test_access_token_is_rejected_as_reset_token():
    from app.application.services.auth_service import create_access_token, decode_token

    with pytest.raises(jwt.InvalidTokenError):
        decode_token(create_access_token(1), "reset")
