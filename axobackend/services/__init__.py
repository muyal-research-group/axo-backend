import axobackend.repositories  as RepositoryX
# UsersRepository,CredentialsRepository
import axobackend.models as ModelX
import axobackend.dto as DtoX
from bson import ObjectId
from option import Result,Ok,Err

from fastapi.security import OAuth2PasswordBearer
from datetime import  timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI,Response,HTTPException
import jwt
from axobackend.models import UserModel,AuthenticationAttemptModel
from axobackend.security import hash_value,verify_password,create_access_token
import os


SECRET_KEY                        = os.environ.get("SECRET_KEY","09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM                         = os.environ.get("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES       = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES","30"))
# oauth2_scheme                     = OAuth2PasswordBearer(tokenUrl="token")
# MONGO_DETAILS                     = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
# client                            = AsyncIOMotorClient(MONGO_DETAILS)
# db                                = client.axo
# user_collection                   = db.get_collection("users")
# credentials_collection            = db.get_collection("credentials")
# authentication_attempt_collection = db.get_collection("authentitcation_attempt")


class UsersService(object):
    def __init__(self, 
        user_repository:RepositoryX.UsersRepository,
        credentials_repository: RepositoryX.CredentialsRepository,
        authentication_attempt_repository:RepositoryX.AuthenticationAttemptRepository
    ):
        self.user_repository        = user_repository
        self.credentials_repository = credentials_repository
        self.authentication_attempt_repository = authentication_attempt_repository
    
    # Fatima - Implementar
    async def login(self, authentication_attemp:DtoX.AuthenticationAttemptDTO):
        try:
            query = {
                "$or": [{"username":authentication_attemp.username }]
            }
            found_user_result = await self.user_repository.find_by_username(username=authentication_attemp.username)
            if found_user_result.is_err:
                detail="Incorrect username or password."
                return Err(Exception(detail))
            found_user = found_user_result.unwrap()
            print("FOUND_FOUSer", found_user)
            if not found_user:
                detail = "User not found."
                return Err(Exception(detail))

            user_id                        = str(found_user["_id"])
            credentials_result                    = await self.credentials_repository.find_one({"user_id": user_id  })
            if credentials_result.is_err:
                return Err(Exception("User's credentials not found, please contact support at support@axo.mx"))

            credentials = credentials_result.unwrap()
            verified                       = await verify_password(stored_value= credentials.get("password",''), provided_value=authentication_attemp.password)
            authentication_attemp_model = ModelX.AuthenticationAttemptModel(
                username=authentication_attemp.username,
                password=await hash_value(value=authentication_attemp.password)
            )
            # ________________________________________________________________________________________
            if verified:
                authentication_attemp_model.status = 1
                result = await self.authentication_attempt_repository.create(authentication_attemp_model)
                                                                    #    .model_dump(by_alias=True, exclude=["authentication_attempt_id"])  )
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    SECRET_KEY=SECRET_KEY,
                    ALGORITHM=ALGORITHM,
                    data={
                        "sub": user_id
                    },
                    expires_delta=access_token_expires
                )
                found_user["token"] = access_token
                first = found_user["first_name"]
                last = found_user["last_name"]
                found_user["initials"] = "{}{}".format(first[0], last[0] ).upper()
                found_user["fullname"] = "{} {}".format(first,last).lower().title()
                found_user["_id"] = user_id
 
                return Ok(found_user)
            # ________________________________________________________________________________________
            authentication_attemp_model.status = -1
            await self.authentication_attempt_repository.create(authentication_attemp_model.model_dump())
            return Err(Exception("Incorrect username or password."))
            # raise HTTPException(
                # status_code=501,
                # detail=""
            # )
            
        except Exception as e:
            return Err(e)
    
    async def create(self,create_user_dto:DtoX.CreateUserDTO)->Result[str,Exception]:
        try:
            
            query = {
                "$or":[
                    {"username":create_user_dto.user.username},
                    {"email":create_user_dto.user.email}
                ]
            }

            found_user_result = await self.user_repository.find_one(
                query= query
            )
            if found_user_result.is_err:
                return found_user_result
            
            found_user = found_user_result.unwrap()

            if found_user:
                return Err(Exception("User already exists."))
            
            user = ModelX.UserModel(
                color         = "",
                disabled      = False,
                email         = create_user_dto.user.email,
                first_name    = create_user_dto.user.first_name,
                last_name     = create_user_dto.user.last_name,
                profile_photo = create_user_dto.user.profile_photo,
                username      = create_user_dto.user.username
            )

            create_user_result = await self.user_repository.create(user=user)
            
            if create_user_result.is_err:
                return create_user_result
            
            user_id = create_user_result.unwrap()
            
            credentials = ModelX.CredentialsModel(
                user_id  = user_id,
                password = create_user_dto.credentials.password,
                pin      = create_user_dto.credentials.pin,
                token    = create_user_dto.credentials.token,
            )

            result = await self.credentials_repository.create(
                credentials=credentials,
            )

            if result.is_err:
                return result
            return Ok(user_id)
       
        except Exception as e:
            return Err(e)