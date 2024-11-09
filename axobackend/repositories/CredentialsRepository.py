from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient
from pymongo.results import InsertOneResult
from typing import Dict,Any
import axobackend.models as ModelX
import axobackend.security as SecurityX
from option import Result,Ok,Err


class CredentialsRepository:
    def __init__(self,
        collection:AsyncIOMotorCollection
    ):
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
            credentials_dict["password"] = await SecurityX.hash_value(credentials_dict.get("password",""))
            credentials_dict["pin"] = await SecurityX.hash_value(credentials_dict.get("pin",""))
            credentials_dict["token"] = await SecurityX.hash_value(credentials_dict.get("token",""))
            result = await self.collection.insert_one(
                credentials_dict
                # credentials.model_dump(by_alias=by_alias)
            )
            return Ok(result)
        except Exception as e:
            return Err(e)