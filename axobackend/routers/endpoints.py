from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories.EndpointsRepository as EndpointsRepository
import axobackend.services.EndpointsServices as EndpointsServices
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, endpoint_collection

endpoint_repository               = EndpointsRepository.EndpointsRepository(
    client     = client,
    collection = endpoint_collection
)
endpoint_service = EndpointsServices.EndpointsService(
    endpoint_repository               = endpoint_repository
)


endpoints_router = APIRouter(
    prefix="/endpoints",
    tags=["Endpoints"],
    responses={403: {"description": "Access forbidden"}}
)

@endpoints_router.get("")
async def get_user_endpoints(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await endpoint_service.get_user_endpoints(current_user.user_id)
        if result.is_ok:
            return {"endpoints": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@endpoints_router.get("/{e_id}")
async def get_endpoint(
    e_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await endpoint_service.get_endpoint(e_id, current_user.user_id)
        
        if result.is_ok:
            endpoint = result.unwrap()
            
            return {"endpoint": endpoint}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="endpoint not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    
@endpoints_router.post("")
async def create_endpoint(
    create_endpoint: DtoX.CreateEndpointDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await endpoint_service.create_endpoint(create_endpoint, current_user.user_id)
    if result.is_ok:
        e_id = result.unwrap()
        return {"e_id": e_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    
@endpoints_router.put("/{e_id}")
async def update_endpoint(
    e_id: str,
    update_endpoint: DtoX.UpdateEndpointDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await endpoint_service.update_endpoint(e_id, current_user.user_id, update_endpoint)
    if result.is_ok:
        return {"message": "Endpoint updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
    
@endpoints_router.delete("/{e_id}")
async def delete_endpoint(
    e_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await endpoint_service.delete_endpoint(e_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Endpoint deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    