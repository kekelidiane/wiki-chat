import logging

from starlette.status import HTTP_403_FORBIDDEN

from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.models.security.auth_user import AuthenticatedUser


def _find_user(args, kwargs) -> AuthenticatedUser | None:
    for value in list(args) + list(kwargs.values()):
        if isinstance(value, AuthenticatedUser):
            return value
    return None


def has_any_roles(logger: logging.Logger, resource: str, roles: list[str]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = _find_user(args, kwargs)
            if user is not None and any(user.has_role(r) for r in roles):
                return await func(*args, **kwargs)
            name = user.username if user else "anonymous"
            logger.error("access denied on %s for user %s", resource, name)
            raise ApiException(
                status_code=HTTP_403_FORBIDDEN,
                error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                message="resource access denied",
            )

        return wrapper

    return decorator
