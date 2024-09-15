from pydantic import BaseModel, Field
from typing import List, Optional,Dict,Any
from bson import ObjectId
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str 


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid object id')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type='string')


class UserModel(BaseModel):
    user_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    profile_photo:Optional[str] =""
    username: str
    email: str
    first_name:str
    last_name:str
    disabled: Optional[bool] = False
    color: Optional[str] = ""
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class CredentialsModel(BaseModel):
    crendentials_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    user_id: str
    password: str
    token: str
    pin:str


class AuthenticationAttemptModel(BaseModel):
    authentication_attempt_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    username:str
    password:str
    status:int # -1 - error 0 - default 1 - success 


class BucketModel(BaseModel):
    bucket_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    alias: str
    user_id: str
    group_id: str

class GroupModel(BaseModel):
    group_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    alias: str

class GroupUserModel(BaseModel):
    group_user_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    group_id: str 
    user_id: str 
class GroupPermissionsModel(BaseModel):
    group_permission_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    alias:str
    value:int

class GroupGroupPermissionModel(BaseModel):
    group_group_permission_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    group_id: str 
    group_permission_id: str

class BucketInfoModel(BaseModel):
    bucket_info_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    group_id: str
    bucket_id:str
    size: float
    num_balls: int
    replicated: bool
# ________________________________________________________

class BallModel(BaseModel):
    ball_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    bucket_id: str
    size:int
    checksum: str
    content_type: str
    name: str
    extension: str
    metadata: Dict[str,Any]
    
class ChunkModel(BaseModel):
    chunk_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    ball_id: str
    index:int
    size:int
    checksum:str
    metadata: Dict[str,Any]

# ________________________________________________________
class RoleModel(BaseModel):
    role_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    display_name:str
    value:str

class PermissionModel(BaseModel):
    permission_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    display_name:str
    value:str

class RolePermissionModel(BaseModel):
    role_permission_id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    role_id: PyObjectId = Field(default_factory=PyObjectId)
    permission_id: PyObjectId = Field(default_factory=PyObjectId)


