from bson import ObjectId
import humanfriendly as HF
from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient,AsyncIOMotorClientSession
from pymongo.results import InsertOneResult, UpdateResult
import axobackend.models as ModelX
from typing import Dict,Any,List,Optional
from option import Result,Ok,Err
from datetime import datetime, timezone

#Task Repository
class TasksRepository:
    def __init__(
        self, 
        client: AsyncIOMotorClient, 
        collection: AsyncIOMotorCollection
    ):
        self.client = client
        self.collection = collection
    
    async def find_one(self, query: Dict[str, Any] = {}) -> Result[Dict[str, Any], Exception]:
        try:
            found_task = await self.collection.find_one(query)
            return Ok(found_task)
        except Exception as e:
            return Err(e)
        
    async def find_by_user_id(self, user_id: str) -> Result[List[Dict[str, Any]], Exception]:
        try:
            query = {"user_id": ObjectId(user_id)}
            cursor = self.collection.find(query)
            found_task = await cursor.to_list(length=100)
            return Ok(found_task)
        except Exception as e:
            return Err(e)
        
    async def create(self, task: ModelX.TaskModel, by_alias: bool = True) -> Result[str, Exception]:
        try:
            task_data = task.model_dump(by_alias=by_alias, exclude=["task_id"])
            
            if "user_id" in task_data and isinstance(task_data["user_id"], str):
                task_data["user_id"] = ObjectId(task_data["user_id"])
                
            if "created_at" not in task_data:
                task_data["created_at"] = datetime.now(timezone.utc)
                
            insert_result = await self.collection.insert_one(task_data)
            return Ok(str(insert_result.inserted_id))
        
        except Exception as e:
            return Err(e)
        
    async def update(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Result[bool, Exception]:
        try:
            query = {
                "_id": ObjectId(task_id),
                "user_id": ObjectId(user_id)
            }
            safe_update_data = update_data.copy()
            for field in ["_id", "user_id", "created_at"]:
                safe_update_data.pop(field, None)
                
            safe_update_data["updated_at"] = datetime.now(timezone.utc)
            
            update_result = await self.collection.update_one(
                query,
                {"$set": safe_update_data}
            )
            
            if update_result.matched_count == 0:
                return Err(ValueError("Task not found or access denied"))
                
            return Ok(update_result.modified_count > 0)
        
        except Exception as e:
            return Err(e)
        
    async def delete(self, task_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            query = {
                "_id": ObjectId(task_id),
                "user_id": ObjectId(user_id)
            }
            
            delete_result = await self.collection.delete_one(query)
            
            if delete_result.deleted_count == 0:
                return Err(ValueError("Task not found or access denied"))
                
            return Ok(True)
            
        except Exception as e:
            return Err(e)
    