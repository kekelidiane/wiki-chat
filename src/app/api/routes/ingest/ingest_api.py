import logging

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.core.exceptions.api_exception import ApiException
from app.core.json.json_response import ORJSONResponse
from app.models.security.auth_user import AuthenticatedUser
from app.security.api_roles import ApiRoles
from app.security.authentication_provider import AUTHENTICATION_PROVIDER
from app.services.factory.services_factory import CHAT_FACTORY, ChatServices

LOGGER = logging.getLogger(__name__)

router = APIRouter()

_ADMIN_ROLES = {ApiRoles.MANAGER, ApiRoles.DIRECTOR}


@router.post("/ingest")
async def ingest(
    services: ChatServices = Depends(CHAT_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    if not _ADMIN_ROLES.intersection(auth_user.roles):
        return ORJSONResponse(
            status_code=HTTP_403_FORBIDDEN, content="resource access denied"
        )
    try:
        result = await services.ingestion_service.reindex()
        return ORJSONResponse(status_code=HTTP_200_OK, content=result)
    except ApiException as exc:
        LOGGER.error("ingest error: %s", exc.message)
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error("unexpected ingest error: %s", exc)
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )
