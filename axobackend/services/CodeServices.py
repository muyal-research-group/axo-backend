import axobackend.repositories  as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List,Optional
from bson import ObjectId

#Code Service        
class CodeService(object):
    def __init__(self, 
        repository: RepositoryX.CodeRepository
    ):
        self.repository        = repository
    
    async def get_user_code(self, user_id:str)->Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            codes = result.unwrap()
    
            for code in codes:
                code["_id"] = str(code["_id"])
                if "user_id" in code and isinstance(code["user_id"], ObjectId):
                    code["user_id"] = str(code["user_id"])
                if "axo_id" in code and isinstance(code["axo_id"], ObjectId):
                    code["axo_id"] = str(code["axo_id"])

            return Ok(codes)
        except Exception as e:
            return Err(e)
        
    async def get_code(self, code_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:

        try:
            query = {
                "_id": ObjectId(code_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result

            code = result.unwrap()
            if not code:
                return Err(ValueError("Code not found"))
            
            code["_id"] = str(code["_id"])
            code["user_id"] = str(code["user_id"])
            code["axo_id"] = str(code["axo_id"])
            
            return Ok(code)
        
        except Exception as e:
            return Err(e)
        
    async def create_code(self, create_code: DtoX.CreateCodeDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            code = ModelX.CodeModel(
                user_id=user_id,
                axo_id=create_code.axo_id,
                code= create_code.code,
                created_at= create_code.created_at
            )
            
            result = await self.repository.create(code)
            
            if result.is_err:
                return result
                
            task_id = result.unwrap()
            return Ok(task_id)
            
        except Exception as e:
            return Err(e)

    async def update_code(self, 
        code_id: str, 
        user_id: str, 
        update_code: DtoX.UpdateCodeDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_code(code_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_code.model_dump(exclude_unset=True)
            
            result = await self.repository.update(code_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_code(self, code_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_code(code_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(code_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)
