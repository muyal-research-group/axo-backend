from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient
from typing import Dict,Any
from option import Ok, Err,Result
from axobackend.utils import Utils 
import axobackend.models as ModelX
class UsersRepository:
    def __init__(
        self,
        collection:AsyncIOMotorCollection
    ):
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