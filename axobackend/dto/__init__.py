from pydantic import BaseModel, Field
from datetime import datetime, timezone
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

class VirtualEnvironmentDTO(BaseModel):
    ve_id: Optional[str] =""
    user_id: Optional[str] =""
    cpu: str
    memory: str
    name: str
    
class CreateVirtualEnvironmentDTO(BaseModel):
    name: str
    cpu: str
    memory: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateVirtualEnvironmentDTO(BaseModel):
    name: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    
class EndpointDTO(BaseModel):
    e_id: Optional[str] = ""
    cpu: str
    memory: str
    
class CreateEndpointDTO(BaseModel):
    ve_id: Optional[str] =""
    cpu: str
    memory: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateEndpointDTO(BaseModel):
    cpu: str
    memory: str
    
class AxoObjectShadowDTO(BaseModel):
    axos_id: Optional[str] = ""
    
class CreateAxoObjectShadowDTO(BaseModel):
    e_id: Optional[str] = ""
    axo_id: Optional[str] = ""
    ve_id: Optional[str] = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateAxoObjectShadowDTO(BaseModel):
    e_id: Optional[str] = ""
    axo_id: Optional[str] = ""
    ve_id: Optional[str] = ""

class AxoObjectDTO(BaseModel):
    axo_id: Optional[str] = ""
    created_at: Optional[str] = ""
    
class CreateAxoObjectDTO(BaseModel):
    code_id: Optional[str] = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateAxoObjectDTO(BaseModel):
    code_id: Optional[str] = ""
    
class CodeDTO(BaseModel):
    code_id: Optional[str] = ""
    code: str
    created_at: Optional[str] = ""
    
class CreateCodeDTO(BaseModel):
    code: str
    axo_id: Optional[str] = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateCodeDTO(BaseModel):
    code: str
    
class ResultDTO(BaseModel):
    result_id: Optional[str] = ""
    hash:str
    created_at: Optional[str] = ""
    
class CreateResultDTO(BaseModel):
    axos_id: Optional[str] = ""
    hash:Optional[str] = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateResultDTO(BaseModel):
    axos_id: Optional[str] = ""
    hash:Optional[str] = ""
    
class TaskDTO(BaseModel):
    task_id: Optional[str] = ""
    created_at: Optional[str] = ""
    
class CreateTaskDTO(BaseModel):
    axos_id: Optional[str] = ""  
    source_bucket_id: Optional[str] = ""
    sink_bucket_id: Optional[str] = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class UpdateTaskDTO(BaseModel):
    axos_id: Optional[str] = ""  
    source_bucket_id: Optional[str] = ""
    sink_bucket_id: Optional[str] = ""
    