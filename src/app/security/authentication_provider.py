import logging

import jwt
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.configs.environment import ENVIRONMENT_CONFIG, EnvKey
from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.models.security.auth_user import AuthenticatedUser
from app.security.api_roles import ApiRoles

LOGGER = logging.getLogger(__name__)


class JwtValidator:
    def __init__(self, config: dict):
        domain = config[EnvKey.WIKI_JWT_AUTHORITY_DOMAIN].rstrip("/")
        realm = config[EnvKey.WIKI_KC_REALM]
        self._issuer = f"{domain}/realms/{realm}"
        self._client_id = config[EnvKey.WIKI_KC_CLIENT_ID]
        self._audience = self._client_id
        self._jwks_client = jwt.PyJWKClient(
            f"{self._issuer}/protocol/openid-connect/certs"
        )

    def validate(self, token: str) -> AuthenticatedUser:
        signing_key = self._jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self._audience,
            issuer=self._issuer,
        )
        roles = (
            claims.get("resource_access", {}).get(self._client_id, {}).get("roles", [])
        )
        return AuthenticatedUser(
            user_id=claims.get("sub", ""),
            username=claims.get("preferred_username", ""),
            email=claims.get("email"),
            roles=roles,
            groups=claims.get("groups", []),
        )


class AuthenticationProvider(HTTPBearer):
    def __init__(self, validator: JwtValidator):
        super().__init__(auto_error=True)
        self._validator = validator

    async def __call__(self, request: Request) -> AuthenticatedUser:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials is None or credentials.scheme != "Bearer":
            raise ApiException(
                status_code=HTTP_401_UNAUTHORIZED,
                error_code=ApiErrorsCode.UNAUTHENTICATED,
                message="invalid authentication scheme",
            )
        try:
            return self._validator.validate(credentials.credentials)
        except Exception as exc:
            LOGGER.error("token validation failed: %s", exc)
            raise ApiException(
                status_code=HTTP_401_UNAUTHORIZED,
                error_code=ApiErrorsCode.UNAUTHENTICATED,
                message="authentication error",
            )


class AuthenticationProviderMock:
    def __call__(self) -> AuthenticatedUser:
        return AuthenticatedUser(
            user_id="test-user",
            username="digijob",
            email="developer@wearedigijob.com",
            roles=[ApiRoles.EMPLOYEE, ApiRoles.MANAGER, ApiRoles.DIRECTOR],
            groups=[],
        )


AUTHENTICATION_PROVIDER = AuthenticationProvider(JwtValidator(ENVIRONMENT_CONFIG))
