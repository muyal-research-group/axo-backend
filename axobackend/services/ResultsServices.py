import axobackend.repositories  as RepositoryX
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List,Optional
from bson import ObjectId

#Results Service        
class ResultsService(object):
    def __init__(self, 
        repository: RepositoryX.ResultsRepository
    ):
        self.repository        = repository
    
    async def get_user_results(self, user_id: str) -> Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            results = result.unwrap()

            for result in results:
                result["_id"] = str(result["_id"])
                if "user_id" in result and isinstance(result["user_id"], ObjectId):
                    result["user_id"] = str(result["user_id"])
                if "axos_id" in result and isinstance(result["axos_id"], ObjectId):
                    result["axos_id"] = str(result["axos_id"])
                
            return Ok(results)

        except Exception as e:
            return Err(e)
        
    async def get_result(self, result_id: str,  user_id: str) -> Result[Dict[str, Any], Exception]:
    
        try:
            query = {
                "_id": ObjectId(result_id),
                "user_id": ObjectId(user_id)
            }
            result = await self.repository.find_one(query)
            
            if result.is_err:
                return result

            result = result.unwrap()
            if not result:
                return Err(ValueError("Results not found"))
            
            result["_id"] = str(result["_id"])
            result["user_id"] = str(result["user_id"])
            result["axos_id"] = str(result["axos_id"])

            return Ok(result)
        
        except Exception as e:
            return Err(e)
        
    async def create_result(self, create_result: DtoX.CreateResultDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            res = ModelX.ResultModel(
                user_id=user_id,
                axos_id=create_result.axos_id,
                hash=create_result.hash,
                created_at= create_result.created_at
            )
            
            result = await self.repository.create(res)
            
            if result.is_err:
                return result
                
            result_id = result.unwrap()
            return Ok(result_id)
            
        except Exception as e:
            return Err(e)

    async def update_result(self, 
        result_id: str, 
        user_id: str, 
        update_result: DtoX.UpdateResultDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_result(result_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_result.model_dump(exclude_unset=True)
            
            result = await self.repository.update(result_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_result(self, result_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_result(result_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.repository.delete(result_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)



