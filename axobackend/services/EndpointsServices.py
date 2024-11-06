import axobackend.repositories  as RepositoryX
import axobackend.repositories.EndpointsRepository as EndpointsRepository
import axobackend.models as ModelX
import axobackend.dto as DtoX
from option import Result,Ok,Err
from typing import Dict,Any,List,Optional
from bson import ObjectId

#Endpoints Service        
class EndpointsService(object):
    def __init__(self, 
        endpoint_repository: EndpointsRepository.EndpointsRepository,
    ):
        self.endpoint_repository        = endpoint_repository
    
    async def get_user_endpoints(self, user_id:str)->Result[List[Dict[str, Any]], Exception]:
        try:
            result = await self.endpoint_repository.find_by_user_id(user_id)
            if result.is_err:
                return result
            endpoints = result.unwrap()
    
            for endpoint in endpoints:
                endpoint["_id"] = str(endpoint["_id"])
                if "user_id" and "ve_id" in endpoint:
                    endpoint["user_id"] = str(endpoint["user_id"])
                    endpoint["ve_id"] = str(endpoint["ve_id"])
        
            return Ok(endpoints)
        
        except Exception as e:
            return Err(e)
    
    async def get_endpoint(self, e_id: str, user_id: str) -> Result[Dict[str, Any], Exception]:
        
        try:
            query = {
                "_id": ObjectId(e_id),
                "user_id": ObjectId(user_id)
            }
            
            result = await self.endpoint_repository.find_one(query)
            
            if result.is_err:
                return result

            endpoint = result.unwrap()
            if not endpoint:
                return Err(ValueError("Endpoint not found"))

            endpoint["_id"] = str(endpoint["_id"])
            endpoint["user_id"] = str(endpoint["user_id"])
            endpoint["ve_id"] = str(endpoint["ve_id"])

            return Ok(endpoint)
        
        except Exception as e:
            return Err(e)
        
    async def create_endpoint(self, create_endpoint: DtoX.CreateEndpointDTO, user_id: str) -> Result[str, Exception]:
        try:
            
            endpoint = ModelX.EndpointModel(
                user_id=user_id,
                ve_id=create_endpoint.ve_id,
                cpu= create_endpoint.cpu,
                memory=create_endpoint.memory,
                created_at= create_endpoint.created_at
            )
            
            result = await self.endpoint_repository.create(endpoint)
            
            if result.is_err:
                return result
                
            e_id = result.unwrap()
            return Ok(e_id)
            
        except Exception as e:
            return Err(e)

    async def update_endpoint(self, 
        e_id: str, 
        user_id: str, 
        update_endpoint: DtoX.UpdateEndpointDTO
    ) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_endpoint(e_id, user_id)
            if exists_result.is_err:
                return exists_result

            update_data = update_endpoint.model_dump(exclude_unset=True)
            
            result = await self.endpoint_repository.update(e_id, user_id, update_data)
            
            if result.is_err:
                return result
                
            success = result.unwrap()
            return Ok(success)
            
        except Exception as e:
            return Err(e)

    async def delete_endpoint(self, e_id: str, user_id: str) -> Result[bool, Exception]:
        try:
            exists_result = await self.get_endpoint(e_id, user_id)
            if exists_result.is_err:
                return exists_result
            
            result = await self.endpoint_repository.delete(e_id, user_id)
            
            if result.is_err:
            
                return result
                
            success = result.unwrap()
            return Ok(success)
        except Exception as e:
            return Err(e)

