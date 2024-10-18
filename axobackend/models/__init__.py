from pydantic import BaseModel, Field,BeforeValidator,ConfigDict
from typing import List, Optional,Dict,Any,Annotated
from bson import ObjectId
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