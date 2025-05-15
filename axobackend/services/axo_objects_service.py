import axobackend.repositories  as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List,Optional
from bson import ObjectId

#Axo Service        
class AxoObjectsService(object):
    def __init__(self, 
        repository: RepositoryX.AxoObjectsRepository
    ):
        self.repository        = repository
    
    async def get_user_axo(self, user_id: str) -> Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            axo_objects = result.unwrap()

            for axo_object in axo_objects:
                axo_object["_id"] = str(axo_object["_id"])
                if "user_id" in axo_object and isinstance(axo_object["user_id"], ObjectId):
                    axo_object["user_id"] = str(axo_object["user_id"])
                if "code_id" in axo_object and isinstance(axo_object["code_id"], ObjectId):
                    axo_object["code_id"] = str(axo_object["code_id"])
                    
            return Ok(axo_objects)

        except Exception as e:
            return Err(e)
        
    async def get_axo_object(self, axo_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:
        try:
            query = {
                "_id": ObjectId(axo_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result

            axo_object = result.unwrap()
            if not axo_object:
                return Err(ValueError("Axo Object not found"))
            
            axo_object["_id"] = str(axo_object["_id"])
            axo_object["user_id"] = str(axo_object["user_id"])
            axo_object["code_id"] = str(axo_object["code_id"])
            
            return Ok(axo_object)
        
        except Exception as e:
            return Err(e)

    async def create_axo_object(self, create_axo: DtoX.CreateAxoObjectDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            axo_object = ModelX.AxoObjectModel(
                user_id=user_id,
                code_id=create_axo.code_id,
                created_at= create_axo.created_at
            )
            
            result = await self.repository.create(axo_object)
            
            if result.is_err:
                return result
                
            axo_id = result.unwrap()
            return Ok(axo_id)
        
        except Exception as e:
            return Err(e)

    async def update_axo_object(self, 
        axo_id: str, 
        user_id: str, 
        update_axo: DtoX.UpdateAxoObjectDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_axo_object(axo_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_axo.model_dump(exclude_unset=True)
            
            result = await self.repository.update(axo_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_axo_object(self, axo_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_axo_object(axo_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(axo_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)


