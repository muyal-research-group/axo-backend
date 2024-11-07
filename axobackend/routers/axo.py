from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories.AxoObjectsRepository as AxoObjectsRepository
import axobackend.services.AxoObjectsServices as AxoObjectsServices
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, axo_object_collection

axo_repository                    = AxoObjectsRepository.AxoObjectsRepository(
    client     = client,
    collection = axo_object_collection
)
axo_service = AxoObjectsServices.AxoObjectsService(
    axo_repository                   = axo_repository
)


axo_router = APIRouter(
    prefix="/axo-objects",
    tags=["Axo Objects"],
    responses={403: {"description": "Access forbidden"}}
)

@axo_router.get("")
async def get_user_axo_objects(current_user: DtoX.UserDTO= Depends(get_current_active_user)):
    try:
        result = await axo_service.get_user_axo(current_user.user_id)
        if result.is_ok:
            return {"axo objects": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@axo_router.get("/{axo_id}")
async def get_axo_object(
    axo_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await axo_service.get_axo_object(axo_id, current_user.user_id)
        
        if result.is_ok:
            axo_object = result.unwrap()
            
            return {"axo object": axo_object}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="axo object not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail="Access denied")


@axo_router.post("")
async def create_axo_object(
    create_axo: DtoX.CreateAxoObjectDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axo_service.create_axo_object(create_axo, current_user.user_id)
    if result.is_ok:
        axo_id = result.unwrap()
        return {"axo_id": axo_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))


@axo_router.put("/{axo_id}")
async def update_axo_object(
    axo_id: str,
    update_axo: DtoX.UpdateAxoObjectDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axo_service.update_axo_object(axo_id, current_user.user_id, update_axo)
    if result.is_ok:
        return {"message": "Axo object updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))


@axo_router.delete("/{axo_id}")
async def delete_axo_object(
    axo_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await axo_service.delete_axo_object(axo_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Axo object deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))