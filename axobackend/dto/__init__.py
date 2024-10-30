from pydantic import BaseModel
from typing import Optional
# from bson import ObjectId
class UserDTO(BaseModel):
    user_id: Optional[str] =""
    profile_photo:Optional[str]=""
    username: str 
    email:str
    first_name:str
    last_name:str
    disabled:Optional[bool]=False

class CredentialsDTO(BaseModel):
    password: str
    pin:Optional[str] =""
    token:Optional[str] =""

class CreateUserDTO(BaseModel):
    user: UserDTO
    credentials:CredentialsDTO

class AuthenticationAttemptDTO(BaseModel):
    username:str
    password:str

class VirtualEnviromentDTO(BaseModel):
    ve_id: Optional[str] =""
    user_id: Optional[str] =""
    cpu: str
    memory: str
    name: str
    
class CreateVirtualEnviromentDTO(BaseModel):
    cpu: str
    memory: str
    name: str

class EndpointDTO(BaseModel):
    e_id: Optional[str] = ""
    cpu: str
    memory: str
    
class CreateEndpointDTO(BaseModel):
    cpu: str
    memory: str
    
class AxoObjectShadowDTO(BaseModel):
    axos_id: Optional[str] = ""
    created_at: Optional[str] = ""

class AxoObjectDTO(BaseModel):
    axo_id: Optional[str] = ""
    created_at: Optional[str] = ""
    
class CodeDTO(BaseModel):
    code_id: Optional[str] = ""
    code: str
    created_at: Optional[str] = ""
    
class CreateCodeDTO(BaseModel):
    code: str
    
class ResultDTO(BaseModel):
    result_id: Optional[str] = ""
    hash:str
    created_at: Optional[str] = ""
    
class TaskDTO(BaseModel):
    task_id: Optional[str] = ""
    created_at: Optional[str] = ""
    