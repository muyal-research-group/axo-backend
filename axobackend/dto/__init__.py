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