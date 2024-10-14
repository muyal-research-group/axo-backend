from fastapi import FastAPI, HTTPException, Depends,Response,status,Query
from fastapi.security import OAuth2PasswordBearer
from datetime import  timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI,Response,HTTPException
import jwt
from typing import Annotated
from axobackend.models import UserModel,AuthenticationAttemptModel
import axobackend.models as ModelX
import axobackend.repositories as RepositoryX
from bson import ObjectId
from axobackend.security import hash_value,verify_password,create_access_token
from jwt.exceptions import InvalidTokenError
import axobackend.dto as DtoX
from fastapi.middleware.cors import CORSMiddleware
import axobackend.services as ServiceX
from fastapi.openapi.utils import get_openapi


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"], # Frontend URL
    allow_credentials = False,
    allow_methods     = ["*"], # Allow all methods (POST, GET, etc.)
    allow_headers     = ["*"], # Allow all headers
)
SECRET_KEY                        = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM                         = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES       = 30
oauth2_scheme                     = OAuth2PasswordBearer(tokenUrl="token")
MONGO_DETAILS                     = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client                            = AsyncIOMotorClient(MONGO_DETAILS)
db                                = client.axo
user_collection                   = db.get_collection("users")
credentials_collection            = db.get_collection("credentials")
authentication_attempt_collection = db.get_collection("authentitcation_attempt")

credentials_respository           = RepositoryX.CredentialsRepository(
    client     = client,
    collection = credentials_collection
)
user_repository                   = RepositoryX.UsersRepository(
    client     = client,
    collection = user_collection
)

users_service = ServiceX.UsersService(
    credentials_repository = credentials_respository,
    user_repository        = user_repository
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = ModelX.TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    
    user_result = await user_repository.find_one(query={"_id": ObjectId(token_data.user_id)})
    if user_result.is_err:
        return credentials_exception
    data = user_result.unwrap()
    print("DATA", data)
    user = DtoX.UserDTO(**data, user_id= str(data["_id"]))
    print("USER", user)
    print("USER_ID", user.user_id)
    # get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



@app.post("/signup")
async def create_user(
    create_user_dto: DtoX.CreateUserDTO
):
    result = await users_service.create(create_user_dto=create_user_dto)

    if result.is_err:
        error = result.unwrap_err()
        raise HTTPException(status_code=500, detail=str(error))
    
    return Response(content=None, status_code=204)



# Auth refactor by Fatima
@app.post("/auth")
async def authenticate(
    authentication_attemp:AuthenticationAttemptModel
):
    result = await users_service.login(authentication_attemp=authentication_attemp)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return Response(content=None, status_code=204)


@app.post("/validate-token")
async def validate_token(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_active_user)],
):
    return Response(content=None, status_code=204)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Axo API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi