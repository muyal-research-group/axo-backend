from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.responses import Response, JSONResponse
import axobackend.dto as DtoX
import axobackend.services as ServiceX
import axobackend.repositories as RepositoryX
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, user_collection, authentication_attempt_collection, credentials_collection

authentication_attempt_repository = RepositoryX.AuthenticationAttemptRepository(
    client=client,
    collection = authentication_attempt_collection
)
credentials_respository           = RepositoryX.CredentialsRepository(
    client     = client,
    collection = credentials_collection
)
user_repository                   = RepositoryX.UsersRepository(
    client     = client,
    collection = user_collection
)
users_service = ServiceX.UsersService(
    credentials_repository            = credentials_respository,
    user_repository                   = user_repository,
    authentication_attempt_repository = authentication_attempt_repository
)


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post("/signup")
async def create_user(
    create_user_dto: DtoX.CreateUserDTO
):
    result = await users_service.create(create_user_dto=create_user_dto)
    if result.is_err:
        error = result.unwrap_err()
        raise HTTPException(status_code=500, detail=str(error))
    return Response(content=None, status_code=204)


@auth_router.post("")
async def authenticate(
    authentication_attemp: DtoX.AuthenticationAttemptDTO
):
    try:
        result = await users_service.login(authentication_attemp=authentication_attemp)
        if result.is_err:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
        return JSONResponse(content=result.unwrap(), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/validate-token")
async def validate_token(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_active_user)],
):
    return Response(content=None, status_code=204)