from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from app.core.json.json_response import ORJSONResponse
from app.services.factory.services_factory import CHAT_FACTORY, ChatServices

router = APIRouter()


@router.get("/health")
async def health(services: ChatServices = Depends(CHAT_FACTORY)):
    result = await services.health_check_service.check()
    return ORJSONResponse(status_code=HTTP_200_OK, content=result)
