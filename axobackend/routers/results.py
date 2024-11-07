from fastapi import APIRouter, Depends, HTTPException
import axobackend.dto as DtoX
import axobackend.repositories.ResultsRepository as ResultsRepository
import axobackend.services.ResultsServices as ResultsServices
from ..dependencies import get_current_user, get_current_active_user
from ..config import client, results_collection

results_repository                = ResultsRepository.ResultsRepository(
    client     = client,
    collection = results_collection
)
results_service = ResultsServices.ResultsService(
    results_repository                = results_repository,
)


results_router = APIRouter(
    prefix="/results",
    tags=["Results"],
    responses={403: {"description": "Access forbidden"}}
)

@results_router.get("")
async def get_user_results(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await results_service.get_user_results(current_user.user_id)
        if result.is_ok:
            return {"results": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@results_router.get("/{result_id}")
async def get_result(
    result_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await results_service.get_result(result_id, current_user.user_id)
        
        if result.is_ok:
            result = result.unwrap()
            
            return {"result": result}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="result not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    
@results_router.post("")
async def create_result(
    create_result: DtoX.CreateResultDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await results_service.create_result(create_result, current_user.user_id)
    if result.is_ok:
        result_id = result.unwrap()
        return {"result_id": result_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    
@results_router.put("/{result_id}")
async def update_result(
    result_id: str,
    update_result: DtoX.UpdateResultDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await results_service.update_result(result_id, current_user.user_id, update_result)
    if result.is_ok:
        return {"message": "Result updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
    
@results_router.delete("/{result_id}")
async def delete_result(
    result_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await results_service.delete_result(result_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Result deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
