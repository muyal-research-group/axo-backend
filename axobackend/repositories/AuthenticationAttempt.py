
from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient
from pymongo.results import InsertOneResult
import axobackend.models as ModelX
from option import Result,Ok,Err

class AuthenticationAttemptRepository:

    def __init__(self, collection:AsyncIOMotorCollection):
        self.collection = collection
    async def create(self, model: ModelX.AuthenticationAttemptModel, by_alias:bool = True)->Result[InsertOneResult,Exception]:
        try:
            x = await self.collection.insert_one(model.model_dump(by_alias=by_alias))
            return Ok(x)
        except Exception as e:
            return Err(e)