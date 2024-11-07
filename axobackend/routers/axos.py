from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories.AxoObjectShadowsRepository as AxoObjectShadowsRepository
import axobackend.services.AxoObjectShadowsServices as AxoObjectShadowsServices
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, axos_collection

axos_repository                   = AxoObjectShadowsRepository.AxoObjectShadowsRepository(
    client     = client,
    collection = axos_collection
)
axos_service = AxoObjectShadowsServices.AxoObjectShadowsService(
    axos_repository                   = axos_repository
)


axos_router = APIRouter(
    prefix="/axo-object-shadows",
    tags=["Axo Object Shadows"],
    responses={403: {"description": "Access forbidden"}}
)

@axos_router.get("")
async def get_user_axos(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await axos_service.get_user_axos(current_user.user_id)
        if result.is_ok:
            return {"axo object shadows": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@axos_router.get("/{axos_id}")
async def get_axos(
    axos_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await axos_service.get_axo_object_shadow(axos_id, current_user.user_id)
        
        if result.is_ok:
            axos = result.unwrap()
            
            return {"axo object shadow": axos}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="axo object shadow not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    
@axos_router.post("")
async def create_axos(
    create_axos: DtoX.CreateAxoObjectShadowDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axos_service.create_axos(create_axos, current_user.user_id)
    if result.is_ok:
        axos_id = result.unwrap()
        return {"axos_id": axos_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    
@axos_router.put("/{axos_id}")
async def update_axos(
    axos_id: str,
    update_axos: DtoX.UpdateAxoObjectShadowDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axos_service.update_axos(axos_id, current_user.user_id, update_axos)
    if result.is_ok:
        return {"message": "Axo object shadow updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
    
@axos_router.delete("/{axos_id}")
async def delete_axos(
    axos_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axos_service.delete_axos(axos_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Axo object shadow deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))