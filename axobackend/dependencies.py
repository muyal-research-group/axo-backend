from fastapi import Depends, HTTPException, status
from typing import Annotated
import jwt
from bson import ObjectId
from jwt import InvalidTokenError
import axobackend.dto as DtoX
import axobackend.models as ModelX
import axobackend.repositories as RepositoryX
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from .config import SECRET_KEY, ALGORITHM, client, user_collection

user_repository                   = RepositoryX.UsersRepository(
    client     = client,
    collection = user_collection
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
        raise credentials_exception
    data = user_result.unwrap()
    user = DtoX.UserDTO(**data, user_id=str(data["_id"]))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
