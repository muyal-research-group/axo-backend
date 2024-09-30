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
    # class Config:
    #     populate_by_name = True
    #     json_encoders = {ObjectId: str}

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

