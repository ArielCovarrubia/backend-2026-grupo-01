import os
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.usuario import Usuario
from app.infrastructure.database import Base, get_db
from app.infrastructure.models import (  # noqa: F401
    CategoriaModel,
    HabitoModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
    RegistroHabitoModel,
    UsuarioModel,
)
from app.infrastructure.repositories import usuario_repository
from app.main import app
from app.presentation.dependencies import get_usuario_actual


@pytest.fixture
def session():
    database_url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    options = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
    if not database_url.startswith("sqlite"):
        options = {}
    engine = create_engine(database_url, **options)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def create_user(session):
    def factory(
        email: str = "ana@x.cl",
        password: str = "example-password-123",
        name: str = "Ana Example",
        role: str = "usuario",
    ) -> Usuario:
        from app.application.services.auth_service import hash_password

        return usuario_repository.guardar(
            Usuario(
                id=0,
                name=name,
                email=email,
                password_hash=hash_password(password),
                role=role,
            ),
            db=session,
        )

    return factory


@pytest.fixture
def admin_user(create_user):
    return create_user(email="admin@x.cl", role="admin")


@pytest.fixture
def user(create_user):
    return create_user()


@pytest.fixture
def access_token(user):
    from app.application.services.auth_service import create_access_token

    return create_access_token(user.id)


@pytest.fixture
def reset_token(user, session):
    from app.application.services.auth_service import create_reset_token

    return create_reset_token(user, session)


@pytest.fixture
def client_sin_login(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()


@pytest.fixture
def client(client_sin_login):
    simulated_user = Usuario(id=0, name="Test Admin", email="admin@x.cl", role="admin")
    app.dependency_overrides[get_usuario_actual] = lambda: simulated_user
    yield client_sin_login
    app.dependency_overrides.pop(get_usuario_actual, None)


@pytest.fixture
def usuario(client_sin_login):
    response = client_sin_login.post(
        "/usuarios/", json={"name": "Patricio", "email": "pato@x.cl"}
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def categoria(client):
    response = client.post(
        "/categorias/", json={"nombre": "Ejercicio", "descripcion": "Physical activity"}
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def habito(client, user, categoria):
    response = client.post(
        "/habitos/",
        json={
            "usuario_id": user.id,
            "categoria_id": categoria["id"],
            "nombre": "Correr",
            "frecuencia_semanal": 3,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def registro(client, habito):
    response = client.post(
        "/registros/",
        json={"habito_id": habito["id"], "fecha_registro": date.today().isoformat()},
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def ayer() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


@pytest.fixture
def manana() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def assert_error(response, status: int, code: str) -> dict:
    assert response.status_code == status, response.text
    body = response.json()
    assert set(body) == {"error"}
    error = body["error"]
    assert error["code"] == code
    assert isinstance(error["message"], str) and error["message"]
    assert isinstance(error["details"], list)
    return error
