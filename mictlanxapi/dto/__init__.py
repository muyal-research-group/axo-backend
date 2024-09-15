from pydantic import BaseModel
# from bson import ObjectId
class UserDTO(BaseModel):
    user_id: str
    profile_photo:str
    username: str 
    email:str
    first_name:str
    last_name:str
    disabled:bool

class BucketDTO(BaseModel):
    bucket_id:str
    alias:str
    user_id:str
    group_id:str
    size:int
    num_balls:int
    replicated:bool