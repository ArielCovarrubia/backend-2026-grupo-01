class DominioException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_RULE_ERROR",
        details: list | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or []


class RecursoNoEncontradoError(DominioException):
    def __init__(
        self,
        message: str = "Recurso no encontrado",
        code: str = "RESOURCE_NOT_FOUND",
        details: list | None = None,
    ):
        super().__init__(message, code=code, details=details)


class ConflictoError(DominioException):
    def __init__(
        self,
        message: str = "Conflicto con el recurso",
        code: str = "CONFLICT",
        details: list | None = None,
    ):
        super().__init__(message, code=code, details=details)


class ReglaNegocioError(DominioException):
    def __init__(
        self,
        message: str = "Violación de regla de negocio",
        code: str = "BUSINESS_RULE_ERROR",
        details: list | None = None,
    ):
        super().__init__(message, code=code, details=details)
