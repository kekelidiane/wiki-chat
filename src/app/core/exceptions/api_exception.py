from enum import Enum


class ApiErrorsCode(str, Enum):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    EMPTY_QUESTION = "EMPTY_QUESTION"
    NO_CONTEXT = "NO_CONTEXT"
    RESOURCE_ACCESS_DENIED = "RESOURCE_ACCESS_DENIED"
    UNAUTHENTICATED = "UNAUTHENTICATED"


class ApiException(Exception):
    def __init__(self, status_code: int, error_code: ApiErrorsCode, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(message)

    @staticmethod
    def server_internal_error() -> dict:
        return {
            "error_code": ApiErrorsCode.INTERNAL_ERROR,
            "message": "internal server error",
        }
