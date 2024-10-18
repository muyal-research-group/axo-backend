from bson import ObjectId
import humanfriendly as HF
from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient,AsyncIOMotorClientSession
from pymongo.results import InsertOneResult
import axobackend.models as ModelX
from typing import Dict,Any,List
from option import Result,Ok,Err
from axobackend.security import hash_value
from axobackend.utils import Utils




class UsersRepository:
    def __init__(
        self,
        client: AsyncIOMotorClient,
        collection:AsyncIOMotorCollection
    ):
        self.client     = client
        self.collection = collection
    
    async def find_one(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    
    async def find_by_username(self,username:str):
        try:
            found_user = await self.find_one({"username": username})
            return found_user
        except Exception as e:
            return Err(e)

    async def create(self,user:ModelX.UserModel,by_alias:bool = True)->Result[str,Exception]:
        try:
            user.color = Utils.get_random_hex_color()
            result = await self.collection.insert_one(user.model_dump(by_alias=by_alias, exclude=["user_id"]))
            return Ok(str(result.inserted_id))
        except Exception as e:
            return Err(e)

class CredentialsRepository:
    def __init__(self,
        client: AsyncIOMotorClient,
        collection:AsyncIOMotorCollection
    ):
        self.client     = client
        self.collection = collection
    
    async def find_one(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def create(self,credentials:ModelX.CredentialsModel,by_alias:bool = True)->Result[InsertOneResult,Exception]:
        try:
            credentials_dict = credentials.model_dump(by_alias=by_alias, exclude=["crendentials_id"])
            credentials_dict["password"] = await hash_value(credentials_dict.get("password",""))
            credentials_dict["pin"] = await hash_value(credentials_dict.get("pin",""))
            credentials_dict["token"] = await hash_value(credentials_dict.get("token",""))
            result = await self.collection.insert_one(
                credentials_dict
                # credentials.model_dump(by_alias=by_alias)
            )
            return Ok(result)
        except Exception as e:
            return Err(e)

class AuthenticationAttemptRepository:

    def __init__(self, client:AsyncIOMotorClient, collection:AsyncIOMotorCollection):
        self.client = client 
        self.collection = collection
    async def create(self, model: ModelX.AuthenticationAttemptModel, by_alias:bool = True)->Result[InsertOneResult,Exception]:
        try:
            x = await self.collection.insert_one(model.model_dump(by_alias=by_alias))
            return Ok(x)
        except Exception as e:
            return Err(e)