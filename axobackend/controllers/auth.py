from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.responses import Response, JSONResponse
import axobackend.dto as DtoX
import axobackend.services as ServiceX
import axobackend.repositories as RepositoryX
import axobackend.db as DbX

from axobackend.dependencies import get_current_user_id, get_current_active_user

USER_COLLECTION = "users"
CREDENTIALS_COLLECTION = "credentials"
AUTHENTICATION_ATTEMPT_COLLECTION = "authentitcation_attempts"



def get_service()->ServiceX.UsersService:
    collection = DbX.get_collection(name=USER_COLLECTION)
    repository = RepositoryX.UsersRepository(collection= collection)

    credentials_repository                   = RepositoryX.CredentialsRepository(
        collection= DbX.get_collection(CREDENTIALS_COLLECTION)
    )
    authentication_attempts_repository = RepositoryX.AuthenticationAttemptRepository(
        collection= DbX.get_collection(AUTHENTICATION_ATTEMPT_COLLECTION)
    )

    service    = ServiceX.UsersService(
        repository                        = repository,
        authentication_attempt_repository = authentication_attempts_repository,
        credentials_repository            = credentials_repository
    )
    return service



auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post("/signup")
async def create_user(
    create_user_dto: DtoX.CreateUserDTO, 
    users_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    result = await users_service.create(create_user_dto=create_user_dto)
    print(result)
    if result.is_err:
        error = result.unwrap_err()
        raise HTTPException(status_code=500, detail=str(error))
    return Response(content=None, status_code=204)


@auth_router.post("")
async def authenticate(
    authentication_attemp: DtoX.AuthenticationAttemptDTO, 
    users_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    try:
        print(authentication_attemp)
        result = await users_service.login(authentication_attemp=authentication_attemp)
        print(result)
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