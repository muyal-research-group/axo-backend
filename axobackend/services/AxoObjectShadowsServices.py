import axobackend.repositories  as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List
from bson import ObjectId

#Axos Service        
class AxoObjectShadowsService(object):
    def __init__(self, 
        repository: RepositoryX.AxoObjectShadowsRepository,
    ):
        self.repository        = repository
    
    async def get_user_axos(self, user_id: str) -> Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            axos = result.unwrap()

            for axo in axos:
                axo["_id"] = str(axo["_id"])
                if "user_id" in axo and isinstance(axo["user_id"], ObjectId):
                    axo["user_id"] = str(axo["user_id"])
                if "e_id" in axo and isinstance(axo["e_id"], ObjectId):
                    axo["e_id"] = str(axo["e_id"])
                if "axo_id" in axo and isinstance(axo["axo_id"], ObjectId):
                    axo["axo_id"] = str(axo["axo_id"])
                if "ve_id" in axo and isinstance(axo["ve_id"], ObjectId):
                    axo["ve_id"] = str(axo["ve_id"])

            return Ok(axos)

        except Exception as e:
            return Err(e)
        
    async def get_axo_object_shadow(self, axos_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:
        try:
            query = {
                "_id": ObjectId(axos_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result

            axos = result.unwrap()
            if not axos:
                return Err(ValueError("Axo Object Shadow not found"))
            
            axos["_id"] = str(axos["_id"])
            axos["user_id"] = str(axos["user_id"])
            axos["e_id"] = str(axos["e_id"])
            axos["axo_id"] = str(axos["axo_id"])
            axos["ve_id"] = str(axos["ve_id"])
            
            return Ok(axos)
        
        except Exception as e:
            return Err(e)
        
    async def create_axos(self, create_axos: DtoX.CreateAxoObjectShadowDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            axos = ModelX.AxoObjectShadowModel(
                user_id=user_id,
                e_id=create_axos.e_id,
                axo_id=create_axos.axo_id,
                ve_id=create_axos.ve_id,
                created_at= create_axos.created_at
            )
            
            result = await self.repository.create(axos)
            
            if result.is_err:
                return result
                
            axos_id = result.unwrap()
            return Ok(axos_id)
        
        except Exception as e:
            return Err(e)

    async def update_axos(self, 
        axos_id: str, 
        user_id: str, 
        update_axos: DtoX.UpdateAxoObjectShadowDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_axo_object_shadow(axos_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_axos.model_dump(exclude_unset=True)
            
            result = await self.repository.update(axos_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_axos(self, axos_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_axo_object_shadow(axos_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(axos_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)


