from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories.VirtualEnvironmentRepository as VirtualEnvironmentRepository
import axobackend.services.VirtualEnvironmentsService as VirtualEnvironmentsService
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, envs_collection

env_repository                    = VirtualEnvironmentRepository.VirtualEnvironmentRepository(
    client     = client,
    collection = envs_collection
)
env_service = VirtualEnvironmentsService.VirtualEnvironmentsService(
    env_repository                   = env_repository
)


environments_router = APIRouter(
    prefix="/virtual-environments",
    tags=["Virtual Environments"],
    responses={403: {"description": "Access forbidden"}}
)

@environments_router.get("")
async def get_user_environments(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await env_service.get_user_environments(current_user.user_id)
        if result.is_ok:
            return {"environments": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@environments_router.get("/{ve_id}")
async def get_environment(
    ve_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await env_service.get_environment(ve_id, current_user.user_id)
        if result.is_ok:
            return {"environment": result.unwrap()}
        else:
            error = result.unwrap_err()
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="Environment not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@environments_router.post("")
async def create_environment(
    create_env_dto: DtoX.CreateVirtualEnvironmentDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await env_service.create_environment(create_env_dto, current_user.user_id)
    if result.is_ok:
        ve_id = result.unwrap()
        return {"ve_id": ve_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))


@environments_router.put("/{ve_id}")
async def update_environment(
    ve_id: str,
    update_env_dto: DtoX.UpdateVirtualEnvironmentDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await env_service.update_environment(ve_id, current_user.user_id, update_env_dto)
    if result.is_ok:
        return {"message": "Environment updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))


@environments_router.delete("/{ve_id}")
async def delete_environment(
    ve_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await env_service.delete_environment(ve_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Environment deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))