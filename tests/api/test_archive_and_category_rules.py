import pytest


def create_category(session, name="Health"):
    from app.application.services.categoria_service import crear_categoria
    from app.presentation.schemas.categoria_schema import CategoriaCreate

    return crear_categoria(
        CategoriaCreate(nombre=name, descripcion="API rule test"), db=session
    )


def create_habit(session, user_id, category_id, name="Walking"):
    from app.application.services.habito_service import crear_habito
    from app.presentation.schemas.habito_schema import HabitoCreate

    return crear_habito(
        HabitoCreate(
            usuario_id=user_id,
            categoria_id=category_id,
            nombre=name,
            frecuencia_semanal=3,
        ),
        db=session,
    )


def headers_for(user_id):
    from app.application.services.auth_service import create_access_token

    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


@pytest.mark.api
def test_category_with_archived_habits_cannot_be_deleted(
    client_sin_login, session, user, admin_user
):
    from app.application.services.habito_service import eliminar_habito
    from app.infrastructure.repositories.categoria_repository import obtener

    category = create_category(session, "Archived habit category")
    habit = create_habit(session, user.id, category.id)
    eliminar_habito(habit.id, db=session)

    response = client_sin_login.delete(
        f"/categorias/{category.id}", headers=headers_for(admin_user.id)
    )

    assert response.status_code == 400
    assert obtener(category.id, db=session) is not None


@pytest.mark.api
def test_category_with_active_habits_cannot_be_deleted(
    client_sin_login, session, user, admin_user
):
    category = create_category(session, "Active habit category")
    create_habit(session, user.id, category.id)

    response = client_sin_login.delete(
        f"/categorias/{category.id}", headers=headers_for(admin_user.id)
    )

    assert response.status_code == 400


@pytest.mark.api
def test_category_without_habits_can_be_deleted(client_sin_login, session, admin_user):
    from app.infrastructure.repositories.categoria_repository import obtener

    category = create_category(session, "Empty category")
    response = client_sin_login.delete(
        f"/categorias/{category.id}", headers=headers_for(admin_user.id)
    )

    assert response.status_code == 204
    assert obtener(category.id, db=session) is None


@pytest.mark.api
def test_archived_habit_can_be_unarchived(client_sin_login, session, user):
    from app.application.services.habito_service import eliminar_habito

    category = create_category(session, "Unarchive category")
    habit = create_habit(session, user.id, category.id)
    eliminar_habito(habit.id, db=session)

    response = client_sin_login.post(
        f"/habitos/{habit.id}/desarchivar", headers=headers_for(user.id)
    )

    assert response.status_code == 200, response.text
    assert response.json()["estado"] == "ACTIVO"


@pytest.mark.api
@pytest.mark.xfail(
    reason="The domain currently reactivates non-archived habits without an error."
)
def test_active_habit_cannot_be_unarchived_again(client_sin_login, session, user):
    category = create_category(session, "Already active category")
    habit = create_habit(session, user.id, category.id)

    response = client_sin_login.post(
        f"/habitos/{habit.id}/desarchivar", headers=headers_for(user.id)
    )

    assert response.status_code == 400


@pytest.mark.api
def test_inactive_category_can_be_activated(client_sin_login, session, admin_user):
    from app.application.services.categoria_service import actualizar_categoria
    from app.infrastructure.repositories.categoria_repository import obtener
    from app.presentation.schemas.categoria_schema import CategoriaUpdate

    category = create_category(session, "Inactive category")
    actualizar_categoria(category.id, CategoriaUpdate(activa=False), db=session)

    response = client_sin_login.post(
        f"/categorias/{category.id}/activar", headers=headers_for(admin_user.id)
    )

    assert response.status_code == 200
    assert obtener(category.id, db=session).activa


@pytest.mark.api
def test_activating_missing_category_returns_not_found(client_sin_login, admin_user):
    response = client_sin_login.post(
        "/categorias/9999/activar", headers=headers_for(admin_user.id)
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.xfail(
    reason="Habit endpoints do not currently enforce resource ownership."
)
def test_user_cannot_unarchive_another_users_habit(
    client_sin_login, session, user, create_user
):
    from app.application.services.habito_service import eliminar_habito

    other_user = create_user(email="other-owner@example.test")
    category = create_category(session, "Other owner category")
    habit = create_habit(session, other_user.id, category.id)
    eliminar_habito(habit.id, db=session)

    response = client_sin_login.post(
        f"/habitos/{habit.id}/desarchivar", headers=headers_for(user.id)
    )

    assert response.status_code in {403, 404}


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", "/habitos/", None),
        ("GET", "/habitos/1", None),
        (
            "POST",
            "/habitos/",
            {
                "usuario_id": 1,
                "categoria_id": 1,
                "nombre": "Sample habit",
                "frecuencia_semanal": 3,
            },
        ),
        ("PUT", "/habitos/1", {"nombre": "Updated habit"}),
        ("DELETE", "/habitos/1", None),
        ("POST", "/habitos/1/desarchivar", None),
        ("GET", "/categorias/", None),
        ("GET", "/categorias/1", None),
        (
            "POST",
            "/categorias/",
            {"nombre": "Sample category", "descripcion": "Test category"},
        ),
        ("PUT", "/categorias/1", {"nombre": "Updated category"}),
        ("DELETE", "/categorias/1", None),
        ("POST", "/categorias/1/activar", None),
        ("GET", "/registros/", None),
        ("GET", "/registros/1", None),
        ("POST", "/registros/", {"habito_id": 1, "fecha_registro": "2026-01-01"}),
        ("PUT", "/registros/1", {"nota": "updated"}),
        ("DELETE", "/registros/1", None),
    ],
)
@pytest.mark.api
def test_habit_category_and_record_routes_require_authentication(
    client_sin_login, method, path, body
):
    response = client_sin_login.request(method, path, json=body)
    assert response.status_code == 401, response.text
