import logging

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from app.api.dto.chat_dto import ChatRequest
from app.core.exceptions.api_exception import ApiException
from app.core.json.json_response import ORJSONResponse
from app.models.security.auth_user import AuthenticatedUser
from app.security.authentication_provider import AUTHENTICATION_PROVIDER
from app.services.factory.services_factory import CHAT_FACTORY, ChatServices

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    services: ChatServices = Depends(CHAT_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        result = await services.rag_service.answer(request.question)
        return ORJSONResponse(status_code=HTTP_200_OK, content=result)
    except ApiException as exc:
        LOGGER.error("chat error: %s", exc.message)
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error("unexpected chat error: %s", exc)
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )
