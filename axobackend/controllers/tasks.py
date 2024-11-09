from fastapi import APIRouter, Depends, HTTPException
from axobackend.dependencies import get_current_active_user
import axobackend.dto as DtoX
import axobackend.repositories as RepositoryX
import axobackend.services as ServiceX
import axobackend.db as DbX

VIRTUAL_ENVIRONMENT_COLLECTION = "virtual_environments"

def get_service()->ServiceX.VirtualEnvironmentsService:
    collection = DbX.get_collection(name=VIRTUAL_ENVIRONMENT_COLLECTION)
    repository = RepositoryX.VirtualEnvironmentRepository(collection= collection)
    service    = ServiceX.VirtualEnvironmentsService(repository= repository)
    return service


tasks_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={403: {"description": "Access forbidden"}}
)

@tasks_router.get("")
async def get_user_tasks(
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    tasks_service:ServiceX.TasksService = Depends(get_service)
):

    try:
        result = await tasks_service.get_user_tasks(current_user.user_id)
        if result.is_ok:
            return {"tasks": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@tasks_router.get("/{task_id}")
async def get_tasks(
    task_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    tasks_service:ServiceX.TasksService = Depends(get_service)
):
    try:
        result = await tasks_service.get_task(task_id, current_user.user_id)
        
        if result.is_ok:
            task = result.unwrap()
            
            return {"task": task}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="result not found")
            raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    
@tasks_router.post("")
async def create_tasks(
    create_tasks: DtoX.CreateTaskDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    tasks_service:ServiceX.TasksService = Depends(get_service)
):
    result = await tasks_service.create_task(create_tasks, current_user.user_id)
    if result.is_ok:
        task_id = result.unwrap()
        return {"result_id": task_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
    
@tasks_router.put("/{task_id}")
async def update_task(
    task_id: str,
    update_tasks: DtoX.UpdateTaskDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    tasks_service:ServiceX.TasksService = Depends(get_service)
):
    result = await tasks_service.update_task(task_id, current_user.user_id, update_tasks)
    if result.is_ok:
        return {"message": "Task updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
    
@tasks_router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user),
    tasks_service:ServiceX.TasksService = Depends(get_service)
):
    result = await tasks_service.delete_task(task_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Task deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=403, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))