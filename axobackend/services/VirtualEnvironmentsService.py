import axobackend.repositories as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result, Ok, Err
from typing import Dict, Any, List
from bson import ObjectId
#VirtualEnviroment Service        
class VirtualEnvironmentsService(object):
    def __init__(self, 
        repository: RepositoryX.VirtualEnvironmentRepository,
    ):
        self.repository        = repository
    
    async def get_user_environments(self, user_id: str)->Result[List[Dict[str, Any]], Exception]:

        try:
            result = await self.repository.find_by_user_id(user_id)
            
            if result.is_err:
                return result
            envs = result.unwrap()
    
            for env in envs:
                env["_id"] = str(env["_id"])
                if "user_id" in env:
                    env["user_id"] = str(env["user_id"])
            
            return Ok(envs)
        
        except Exception as e:
            return Err(e)
        
    async def get_environment(self, ve_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:
        try:
            query = {
                "_id": ObjectId(ve_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result
            
            env = result.unwrap()
            if not env:
                return Err(ValueError("Virtual Environment not found"))

            env["_id"] = str(env["_id"])
            env["user_id"] = str(env["user_id"])
            
            return Ok(env)
                
        except Exception as e:
            return Err(e)
        
    async def create_environment(self, create_env_dto: DtoX.CreateVirtualEnvironmentDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            virtual_env = ModelX.VirtualEnvironmentModel(
                user_id=user_id,
                name= create_env_dto.name,
                cpu= create_env_dto.cpu,
                memory=create_env_dto.memory,
                created_at= create_env_dto.created_at
            )
            
            result = await self.repository.create(virtual_env)
            
            if result.is_err:
                return result
                
            ve_id = result.unwrap()
            return Ok(ve_id)
            
        except Exception as e:
    
            return Err(e)

    async def update_environment(self, 
        ve_id: str, 
        user_id: str, 
        update_env_dto: DtoX.UpdateVirtualEnvironmentDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_environment(ve_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_env_dto.model_dump(exclude_unset=True)
            
            result = await self.repository.update(ve_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_environment(self, ve_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_environment(ve_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(ve_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)