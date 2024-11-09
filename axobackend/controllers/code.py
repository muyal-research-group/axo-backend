from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories as RepositoryX
import axobackend.services as ServiceX
import axobackend.db as DbX
from  axobackend.dependencies import get_current_active_user


CODE_COLLECTION = "codes"

def get_service()->ServiceX.CodeService:
    collection = DbX.get_collection(name=CODE_COLLECTION)
    repository = RepositoryX.CodeRepository(collection= collection)
    service    = ServiceX.CodeService(repository= repository)
    return service


code_router = APIRouter(
    prefix="/code",
    tags=["Code"],
    responses={403: {"description": "Access forbidden"}}
)

@code_router.get("")
async def get_user_code(
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    code_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    try:
        result = await code_service.get_user_code(current_user.user_id)
        if result.is_ok:
            return {"code": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@code_router.get("/{code_id}")
async def get_code(
    code_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    code_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    try:
        result = await code_service.get_code(code_id, current_user.user_id)
        
        if result.is_ok:
            code = result.unwrap()
            
            return {"code": code}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="code not found")
            raise HTTPException(status_code=500, detail=str(error)) 
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    
@code_router.post("")
async def create_code(
    create_code: DtoX.CreateCodeDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    code_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    result = await code_service.create_code(create_code, current_user.user_id)
    if result.is_ok:
        code_id = result.unwrap()
        return {"code_id": code_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    
@code_router.put("/{code_id}")
async def update_code(
    code_id: str,
    update_code: DtoX.UpdateCodeDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    code_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    result = await code_service.update_code(code_id, current_user.user_id, update_code)
    if result.is_ok:
        return {"message": "Code updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
    
@code_router.delete("/{code_id}")
async def delete_code(
    code_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    code_service:ServiceX.VirtualEnvironmentsService = Depends(get_service)
):
    result = await code_service.delete_code(code_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Code deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))