from pydantic import BaseModel, Field,BeforeValidator,ConfigDict
from typing import List, Optional,Dict,Any,Annotated
from datetime import datetime, timezone

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str 


PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    user_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    profile_photo:Optional[str] = None
    username: str
    email: str
    first_name:str
    last_name:str
    disabled: Optional[bool] = False
    color: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name=True,
        #  json_encoders={ObjectId: str},
        arbitrary_types_allowed=True)

class CredentialsModel(BaseModel):
    crendentials_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    user_id: str
    password: str
    token: str
    pin:str
    model_config = ConfigDict(
        populate_by_name=True,
        #  json_encoders={ObjectId: str},
        arbitrary_types_allowed=True)


class AuthenticationAttemptModel(BaseModel):
    authentication_attempt_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    username:str
    password:str
    status:Optional[int] = " " # -1 - error 0 - default 1 - success 
    model_config = ConfigDict(
        populate_by_name=True,
        #  json_encoders={ObjectId: str},
        arbitrary_types_allowed=True)
    
class VirtualEnvironmentModel(BaseModel):
    ve_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    cpu: str
    memory: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    name: str
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class EndpointModel(BaseModel):
    e_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    ve_id: str
    user_id: str
    cpu: str
    memory: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    max_idle_time: Optional[int] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class AxoObjectShadowModel(BaseModel):
    axos_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    e_id: str  
    axo_id: str  
    ve_id: str  
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str 
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class AxoObjectModel(BaseModel):
    axo_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    user_id: str
    code_id: str 
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class CodeModel(BaseModel):
    code_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    axo_id: str
    user_id: str  
    code: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ResultModel(BaseModel):
    result_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    axos_id: str
    user_id: str  
    hash: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class TaskModel(BaseModel):
    task_id: Optional[PyObjectId] = Field(default=None, alias='_id')
    axos_id: str  
    source_bucket_id: str
    sink_bucket_id: str
    user_id: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
