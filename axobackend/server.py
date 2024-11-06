from fastapi import FastAPI, HTTPException, Depends,Response,status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI,Response,HTTPException
import jwt
from typing import Annotated
import axobackend.models as ModelX
import axobackend.repositories as RepositoryX
from bson import ObjectId
from jwt.exceptions import InvalidTokenError
import axobackend.dto as DtoX
from fastapi.middleware.cors import CORSMiddleware
import axobackend.services as ServiceX
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import os
import logging
from bson import ObjectId
import axobackend.repositories.VirtualEnvironmentRepository as VirtualEnvironmentRepository
import axobackend.repositories.EndpointsRepository as EndpointsRepository
import axobackend.repositories.AxoObjectShadowsRepository as AxoObjectShadowsRepository
import axobackend.repositories.AxoObjectsRepository as AxoObjectsRepository
import axobackend.repositories.ResultsRepository as ResultsRepository
import axobackend.repositories.TasksRepository as TasksRepository
import axobackend.repositories.CodeRepository as CodeRepository
import axobackend.services.VirtualEnvironmentsService as VirtualEnvironmentsService
import axobackend.services.EndpointsServices as EndpointsServices
import axobackend.services.AxoObjectShadowsServices as AxoObjectShadowsServices
import axobackend.services.AxoObjectsServices as AxoObjectsServices
import axobackend.services.ResultsServices as ResultsServices
import axobackend.services.TasksServices as TasksServices
import axobackend.services.CodeServices as CodeServices



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"], # Frontend URL
    allow_credentials = False,
    allow_methods     = ["*"], # Allow all methods (POST, GET, etc.)
    allow_headers     = ["*"], # Allow all headers
)
SECRET_KEY                        = os.environ.get("SECRET_KEY","09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM                         = os.environ.get("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES       = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES","30"))
oauth2_scheme                     = OAuth2PasswordBearer(tokenUrl="token")
MONGO_DETAILS                     = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client                            = AsyncIOMotorClient(MONGO_DETAILS)
db                                = client.axo
user_collection                   = db.get_collection("users")
credentials_collection            = db.get_collection("credentials")
authentication_attempt_collection = db.get_collection("authentitcation_attempt")
envs_collection                   = db.get_collection("virtual_environments")
endpoint_collection               = db.get_collection("endpoints")
axos_collection                   = db.get_collection("axos")
axo_object_collection             = db.get_collection("axo_objects")
results_collection                = db.get_collection("results")
tasks_collection                  = db.get_collection("tasks")
code_collection                   = db.get_collection("code")

authentication_attempt_repository = RepositoryX.AuthenticationAttemptRepository(
    client=client,
    collection = authentication_attempt_collection
)
credentials_respository           = RepositoryX.CredentialsRepository(
    client     = client,
    collection = credentials_collection
)
user_repository                   = RepositoryX.UsersRepository(
    client     = client,
    collection = user_collection
)
env_repository                    = VirtualEnvironmentRepository.VirtualEnvironmentRepository(
    client     = client,
    collection = envs_collection
)
endpoint_repository               = EndpointsRepository.EndpointsRepository(
    client     = client,
    collection = endpoint_collection
)
axos_repository                   = AxoObjectShadowsRepository.AxoObjectShadowsRepository(
    client     = client,
    collection = axos_collection
)
axo_repository                    = AxoObjectsRepository.AxoObjectsRepository(
    client     = client,
    collection = axo_object_collection
)
results_repository                = ResultsRepository.ResultsRepository(
    client     = client,
    collection = results_collection
)
tasks_repository                  = TasksRepository.TasksRepository(
    client     = client,
    collection = tasks_collection
)
code_repository                  = CodeRepository.CodeRepository(
    client     = client,
    collection = code_collection
)

users_service = ServiceX.UsersService(
    credentials_repository            = credentials_respository,
    user_repository                   = user_repository,
    authentication_attempt_repository = authentication_attempt_repository
)
env_service = VirtualEnvironmentsService.VirtualEnvironmentsService(
    env_repository                   = env_repository
)
endpoint_service = EndpointsServices.EndpointsService(
    endpoint_repository               = endpoint_repository
)
axos_service = AxoObjectShadowsServices.AxoObjectShadowsService(
    axos_repository                   = axos_repository
)
axo_service = AxoObjectsServices.AxoObjectsService(
    axo_repository                   = axo_repository
)
results_service = ResultsServices.ResultsService(
    results_repository                = results_repository,
)
tasks_service = TasksServices.TasksService(
    tasks_repository                  = tasks_repository
)
code_service = CodeServices.CodeService(
    code_repository                   = code_repository
)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = ModelX.TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    
    user_result = await user_repository.find_one(query={"_id": ObjectId(token_data.user_id)})
    if user_result.is_err:
        return credentials_exception
    data = user_result.unwrap()
    user = DtoX.UserDTO(**data, user_id= str(data["_id"]))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



@app.post("/signup")
async def create_user(
    create_user_dto: DtoX.CreateUserDTO
):
    result = await users_service.create(create_user_dto=create_user_dto)

    if result.is_err:
        error = result.unwrap_err()
        raise HTTPException(status_code=500, detail=str(error))
    
    return Response(content=None, status_code=204)



# Auth refactor by Fatima
@app.post("/auth")
async def authenticate(
    authentication_attemp:DtoX.AuthenticationAttemptDTO
):
    try:
        result = await users_service.login(authentication_attemp=authentication_attemp)
        print("RESULT",result)
        if result.is_err:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

        return JSONResponse(content=result.unwrap(), status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   



@app.post("/validate-token")
async def validate_token(
    current_user: Annotated[DtoX.UserDTO, Depends(get_current_active_user)],
):
    return Response(content=None, status_code=204)

@app.get("/virtual-environments")
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
    
@app.get("/virtual-environments/{ve_id}")
async def get_environment(
    ve_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await env_service.get_environment(ve_id, current_user.user_id)
        
        if result.is_ok:
            environment = result.unwrap()
            
            return {"environment": environment}
        else:
            error = result.unwrap_err()
            
            if isinstance(error, ValueError):
                raise HTTPException(status_code=404, detail="Environment not found")
            raise HTTPException(status_code=500, detail=str(error))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/virtual-environments")
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
    
@app.put("/virtual-environments/{ve_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/virtual-environments/{ve_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/endpoints")
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
    
@app.get("/endpoints/{e_id}")
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/endpoints")
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
    
@app.put("/endpoints/{e_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/endpoints/{e_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.get("/axo-object-shadows")
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
    
@app.get("/axo-object-shadows/{axos_id}")
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/axo-object-shadows")
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
    
@app.put("/axo-object-shadows/{axos_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/axo-object-shadows/{axos_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.get("/axo-objects")
async def get_user_axo_objects(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await axo_service.get_user_axo(current_user.user_id)
        if result.is_ok:
            return {"axo objects": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/axo-objects/{axo_id}")
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/axo-objects")
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
    
@app.put("/axo-objects/{axo_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/axo-objects/{axo_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.get("/results")
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
    
@app.get("/results/{result_id}")
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/results")
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
    
@app.put("/results/{result_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/results/{result_id}")
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
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.get("/tasks")
async def get_user_tasks(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await tasks_service.get_user_tasks(current_user.user_id)
        if result.is_ok:
            return {"tasks": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/tasks/{task_id}")
async def get_tasks(
    task_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/tasks")
async def create_tasks(
    create_tasks: DtoX.CreateTaskDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await tasks_service.create_task(create_tasks, current_user.user_id)
    if result.is_ok:
        task_id = result.unwrap()
        return {"result_id": task_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
@app.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    update_tasks: DtoX.UpdateTaskDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await tasks_service.update_task(task_id, current_user.user_id, update_tasks)
    if result.is_ok:
        return {"message": "Task updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await tasks_service.delete_task(task_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Task deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/code")
async def get_user_code(
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    try:
        result = await code_service.get_user_code(current_user.user_id)
        if result.is_ok:
            return {"code": result.unwrap()}
        else:
            raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/code/{code_id}")
async def get_code(
    code_id: str, 
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
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
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/code")
async def create_code(
    create_code: DtoX.CreateCodeDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await code_service.create_code(create_code, current_user.user_id)
    if result.is_ok:
        code_id = result.unwrap()
        return {"code_id": code_id}
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    
@app.put("/code/{code_id}")
async def update_code(
    code_id: str,
    update_code: DtoX.UpdateCodeDTO,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await code_service.update_code(code_id, current_user.user_id, update_code)
    if result.is_ok:
        return {"message": "Code updated successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))
    
@app.delete("/code/{code_id}")
async def delete_code(
    code_id: str,
    current_user: DtoX.UserDTO = Depends(get_current_active_user)
):
    result = await code_service.delete_code(code_id, current_user.user_id)
    if result.is_ok:
        return {"message": "Code deleted successfully"}
    else:
        error = result.unwrap_err()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=404, detail=str(error))
        raise HTTPException(status_code=500, detail=str(error))

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Axo API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi