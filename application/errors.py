class DomainError(Exception):
    error_code: str = "DOMAIN_ERROR"
    message: str = "Error de dominio"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class ValidationError(DomainError):
    error_code = "INVALID_ARGUMENT"
    message = "Argumentos inválidos."


class NotFoundError(DomainError):
    error_code = "NO_DATA"
    message = "No hay datos para la consulta. Resultado válido, no es un fallo."


class AuthorizationError(DomainError):
    error_code = "FORBIDDEN"
    message = "No autorizado."


class InfrastructureError(DomainError):
    error_code = "UNAVAILABLE"
    message = "No se pudo consultar la fuente de datos. Reintenta; si persiste, escala a TI."


HTTP_STATUS_BY_ERROR = {
    ValidationError: 400,
    NotFoundError: 404,
    AuthorizationError: 403,
    InfrastructureError: 503,
}