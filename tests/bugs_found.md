# QA findings

## Pending dependencies

- `app/presentation/schemas/auth_schema.py` does not define `RegistroDTO`; the requested 12-character minimum and forbidden-extra-field contract is not yet available. The matching tests are expected failures until the auth DTO is added.
- `app/domain/exceptions.py` does not define `TokenInvalido`; token decoding currently raises PyJWT exceptions. Its dedicated-domain-exception test is expected to fail until the auth contract is added.
- `app/application/services/auth_service.py` exposes module-level helpers but no `AuthService` class or repository-based login flow. Mocked service scenarios are pending that interface.
- `Usuario` and `RefreshTokenModel` currently lack lockout state and refresh-token family identifiers. Lockout and family reuse checks are pending those persistence fields and service behavior.
- `app/application/services/auth_service.py` has no repository-injected `AuthService`, and there is no `RefreshToken` domain entity or `esta_vigente()` method. The requested mocked service and domain-token checks are expected failures until those interfaces exist.
- The API currently exposes `/auth/forgot-password` and `/auth/reset-password`; the requested localized recovery routes and `/auth/logout-todos` are not present.

## Confirmed findings

- `app/domain/habito.py`, `test_active_habit_cannot_be_unarchived_again`: expected HTTP 400 when asking to unarchive an already active habit; actual `desarchivar()` unconditionally assigns `ACTIVO`, so the route succeeds. The regression case is marked xfail.
- `app/presentation/routers/habitos.py`, `test_user_cannot_unarchive_another_users_habit`: expected 403 or 404 for a habit owned by another user; actual route passes the ID directly to the service without checking ownership. The regression case is marked xfail.
