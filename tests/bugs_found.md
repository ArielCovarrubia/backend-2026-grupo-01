# Hallazgos de QA

## Dependencias pendientes

- `app/presentation/schemas/auth_schema.py` aún no define `RegistroDTO`; no está disponible el contrato solicitado de mínimo 12 caracteres y rechazo de campos adicionales. Las pruebas correspondientes quedan como fallas esperadas hasta que se agregue el DTO de autenticación.
- `app/domain/exceptions.py` aún no define `TokenInvalido`; la decodificación actual lanza excepciones de PyJWT. La prueba para la excepción de dominio queda como falla esperada hasta que se incorpore el contrato de autenticación.
- `app/application/services/auth_service.py` expone funciones de módulo, pero no una clase `AuthService` ni un flujo de inicio de sesión que reciba repositorios. Las pruebas de servicio con repositorios simulados quedan pendientes de esa interfaz.
- `Usuario` y `RefreshTokenModel` aún no incluyen estado de bloqueo ni identificadores de familia para tokens de actualización. Las pruebas de bloqueo y detección de reutilización quedan pendientes de esos campos y del comportamiento correspondiente.
- `app/application/services/auth_service.py` aún no tiene un `AuthService` que reciba repositorios; tampoco existe una entidad de dominio `RefreshToken` ni el método `esta_vigente()`. Las pruebas solicitadas para el servicio y el estado del token quedan como fallas esperadas hasta que se agreguen esas interfaces.
- La API expone `/auth/forgot-password` y `/auth/reset-password`; aún no están disponibles las rutas localizadas solicitadas, `/auth/logout-todos`, `/auth/me` ni `/health`. La colección incluye las rutas actuales de recuperación y verificaciones para las rutas solicitadas que faltan.

## Hallazgos confirmados

- `app/domain/habito.py`, `test_active_habit_cannot_be_unarchived_again`: se esperaba HTTP 400 al intentar desarchivar un hábito que ya está activo; actualmente `desarchivar()` siempre asigna `ACTIVO` y la ruta responde HTTP 200. La prueba de regresión está marcada como falla esperada.
- `app/presentation/routers/habitos.py`, `test_user_cannot_unarchive_another_users_habit`: se esperaba HTTP 403 o 404 para un hábito de otra persona; actualmente la ruta envía el ID al servicio sin verificar la propiedad del recurso. La prueba de regresión está marcada como falla esperada.
