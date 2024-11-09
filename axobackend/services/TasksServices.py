import axobackend.repositories  as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List,Optional
from bson import ObjectId

#Tasks Service        
class TasksService(object):
    def __init__(self, 
        repository: RepositoryX.TasksRepository
    ):
        self.repository        = repository
    
    async def get_user_tasks(self, user_id:str)->Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            tasks = result.unwrap()
    
            for task in tasks:
                task["_id"] = str(task["_id"])
                if "user_id" in task and isinstance(task["user_id"], ObjectId):
                    task["user_id"] = str(task["user_id"])
                if "axos_id" in task and isinstance(task["axos_id"], ObjectId):
                    task["axos_id"] = str(task["axos_id"])
                if "source_bucket_id" in task and isinstance(task["source_bucket_id"], ObjectId):
                    task["source_bucket_id"] = str(task["source_bucket_id"])
                if "sink_bucket_id" in task and isinstance(task["sink_bucket_id"], ObjectId):
                    task["sink_bucket_id"] = str(task["sink_bucket_id"])
                
            return Ok(tasks)
        except Exception as e:
            return Err(e)
        
    async def get_task(self, task_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:
        
        try:
            query = {
                "_id": ObjectId(task_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result

            task = result.unwrap()
            if not task:
                return Err(ValueError("Task not found"))
            
            
            task["_id"] = str(task["_id"])
            task["user_id"] = str(task["user_id"])
            task["axos_id"] = str(task["axos_id"])
            task["source_bucket_id"] = str(task["source_bucket_id"])
            task["sink_bucket_id"] = str(task["sink_bucket_id"])
            
            return Ok(task)
        
        except Exception as e:
            return Err(e)
        
    async def create_task(self, create_task: DtoX.CreateTaskDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            task = ModelX.TaskModel(
                user_id=user_id,
                axos_id=create_task.axos_id,
                source_bucket_id= create_task.source_bucket_id,
                sink_bucket_id=create_task.sink_bucket_id,
                created_at= create_task.created_at
            )
            
            result = await self.repository.create(task)
            
            if result.is_err:
                return result
                
            task_id = result.unwrap()
            return Ok(task_id)
            
        except Exception as e:
            return Err(e)

    async def update_task(self, 
        task_id: str, 
        user_id: str, 
        update_task: DtoX.UpdateTaskDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_task(task_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_task.model_dump(exclude_unset=True)
            
            result = await self.repository.update(task_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_task(self, task_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_task(task_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(task_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)
