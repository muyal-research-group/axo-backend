from fastapi import Depends, HTTPException, status
from typing import Annotated
import jwt
from bson import ObjectId
from jwt import InvalidTokenError
import os
import axobackend.dto as DtoX
import axobackend.db as DbX
import axobackend.models as ModelX
import axobackend.repositories as RepositoryX
import axobackend.services as ServiceX
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# from .config import SECRET_KEY, ALGORITHM, client, user_collection


ACCESS_TOKEN_EXPIRE_MINUTES:str =os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES","15m")
SECRET_KEY:str =os.environ.get("SECRET","09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM:str =os.environ.get("ALGORITHM","HS256")
async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    collection      = DbX.get_collection("users")
    user_repository = RepositoryX.UsersRepository(
        collection = collection
    )
    users_service = ServiceX.UsersService(
        repository= user_repository,
        authentication_attempt_repository= None,
        credentials_repository= None

    )
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
    
    user_result = await users_service.find_by_user_id(user_id= user_id)
    if user_result.is_err:
        raise credentials_exception
    user = user_result.unwrap()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_user_id)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
