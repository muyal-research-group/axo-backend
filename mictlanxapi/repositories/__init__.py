
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection,AsyncIOMotorClient
from pymongo.results import InsertOneResult
import mictlanxapi.models as ModelX
from typing import Dict,Any,Tuple,List
from option import Result,Ok,Err
from mictlanxapi.security import hash_value,verify_password
from mictlanxapi.dto import BucketDTO
from mictlanxapi.utils import get_random_hex_color

class GroupRepository:
    def __init__(self, 
        client: AsyncIOMotorClient,
        group_collection: AsyncIOMotorCollection,
        group_user_collection: AsyncIOMotorCollection,
    ):
        self.client                = client
        self.group_collection      = group_collection
        self.group_user_collection = group_user_collection
    async def create(self,user_id:str,group:ModelX.GroupModel,by_alias:bool = True):
        try:
            async with await self.client.start_session() as session:
                async with session.start_transaction():
                    await self.group_collection.insert_one(group.model_dump(by_alias=by_alias), session=session)
                    group_user_data = ModelX.GroupUserModel(group_id=str(group.group_id), user_id=user_id).model_dump(by_alias=by_alias)
                    await self.group_user_collection.insert_one(
                        group_user_data,
                        session=session
                    )
                    return Ok(str(group.group_id))
        except Exception as e:
            return Err(e)
    async def delete_by_id(self, group_id:str):
        try:
            async with await self.client.start_session() as session:
                async with  session.start_transaction():
                    self.group_collection.delete_one(filter={"_id":ObjectId(group_id)})
                    self.group_user_collection.delete_one(filter={"group_id": group_id})
        except Exception as e:
            return Err(e)



class UserRepository:
    def __init__(
        self,
        client: AsyncIOMotorClient,
        collection:AsyncIOMotorCollection
    ):
        self.client     = client
        self.collection = collection
    async def find_one(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def create(self,user:ModelX.UserModel,by_alias:bool = True)->Result[Any,Exception]:
        try:
            user.color = get_random_hex_color()
            result = await self.collection.insert_one(user.model_dump(by_alias=by_alias))
            return Ok(result)
        except Exception as e:
            return Err(e)
class CredentialsRepository:
    def __init__(self,
        client: AsyncIOMotorClient,
        collection:AsyncIOMotorCollection
    ):
        self.client     = client
        self.collection = collection
    
    async def find_one(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def create(self,credentials:ModelX.CredentialsModel,by_alias:bool = True)->Result[InsertOneResult,Exception]:
        try:
            credentials_dict = credentials.model_dump(by_alias=by_alias)
            credentials_dict["password"] = await hash_value(credentials_dict.get("password",""))
            credentials_dict["pin"] = await hash_value(credentials_dict.get("pin",""))
            credentials_dict["token"] = await hash_value(credentials_dict.get("token",""))
            result = await self.collection.insert_one(
                credentials_dict
                # credentials.model_dump(by_alias=by_alias)
            )
            return Ok(result)
        except Exception as e:
            return Err(e)


class BucketRepository:
    def __init__(self,
        client: AsyncIOMotorClient,
        bucket_collection:AsyncIOMotorCollection,
        bucket_info_collection:AsyncIOMotorCollection
    ):
        self.client                 = client
        self.bucket_collection      = bucket_collection
        self.bucket_info_collection = bucket_info_collection
    
    async def find_one_bucket(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.bucket_collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def find_one_bucket_by_alias(self,alias:str ):
        try:
            found_user = await self.bucket_collection.find_one({"alias":alias})
            return Ok(found_user)
        except Exception as e:
            return Err(e)
        
    async def create(self, bucket:ModelX.BucketModel, group_id:str,by_alias:bool = True)->Result[str,Exception]:
        try:
            async with await self.client.start_session() as session:
                async with  session.start_transaction():
                    bucket.group_id = group_id
                    bucket_data = bucket.model_dump(by_alias=by_alias)
                    await self.bucket_collection.insert_one(bucket_data,session=session)
                    bucket_info = ModelX.BucketInfoModel(group_id=group_id, bucket_id=str(bucket.bucket_id),size=0, num_balls=0, replicated=False).model_dump(by_alias=by_alias)
                    await self.bucket_info_collection.insert_one(bucket_info,session=session)
                    return Ok(str(bucket.bucket_id))
        except Exception as e:
            return Err(e)
    async def find_all(self,query:Dict[str,Any]={},skip:int=0, limit:int=10):
        try:
            async with await self.client.start_session() as session:
                async with  session.start_transaction():
                    buckets = self.bucket_collection.find(query).skip(skip=skip).limit(limit=limit)
                    return Ok(buckets)
        except Exception as e:
            return Err(e)
    async def find_buckets_and_infos_all(self,query:Dict[str,Any]={},skip:int=0, limit:int=10)->Result[List[BucketDTO], Exception]:
        try:
            async with await self.client.start_session() as session:
                async with  session.start_transaction():
                    cursor = self.bucket_collection.find(query).skip(skip=skip).limit(limit=limit)
                    bs = []
                    async for bucket in cursor:
                        bucket_info = await self.bucket_info_collection.find_one({"bucket_id":str(bucket["_id"])})
                        b = BucketDTO(
                            bucket_id= str(bucket["_id"]),
                            alias=bucket["alias"],
                            user_id= bucket["user_id"],
                            group_id= bucket["group_id"],
                            num_balls=bucket_info["num_balls"],
                            replicated=bucket_info["replicated"],
                            size=bucket_info["size"],
                            
                        )
                        bs.append(b)
                    return Ok(bs)
        except Exception as e:
            return Err(e)

    async def delete(self,bucket_id:str):
        try:
            async with await self.client.start_session() as session:
                async with  session.start_transaction():
                    buckets = await self.bucket_collection.delete_one(filter={"bucket_id":ObjectId(bucket_id)})
                    return Ok(buckets)
        except Exception as e:
            return Err(e)
        
class BallRepository:
    def __init__(self,
        client: AsyncIOMotorClient,
        ball_collection:AsyncIOMotorCollection,
    ):
        self.client          = client
        self.ball_collection = ball_collection
    
    async def find_balls_by_bucket_id(self,bucket_id:str):
        try:
            query = {"bucket_id":bucket_id}
            result = self.ball_collection.find(query)
            bs=[]
            async for ball in result:
                ball["_id"]=str(ball["_id"])
                bs.append(ball)
            return Ok(bs)
        except Exception as e:
            return Err(e)
        
    async def find_one_ball(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.ball_collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def find_by_ball_id(self,ball_id:str):
        try:
            # found_user = await self.ball_collection.find_one(query)
            return await self.find_one_ball({"_id":ObjectId(ball_id)})
            # return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def create(self,ball:ModelX.BallModel,by_alias:bool=True)->Result[InsertOneResult,Exception]:
        try:
            ball_data = ball.model_dump(by_alias=by_alias)
            result    = await self.ball_collection.insert_one(ball_data)
            return Ok(result)
        except Exception as e:
            return Err(e)
class ChunkRepository:
    def __init__(self,
        client: AsyncIOMotorClient,
        chunk_collection:AsyncIOMotorCollection,
    ):
        self.client          = client
        self.chunk_collection = chunk_collection
    
    async def find_chunks_by_ball_id(self,ball_id:str):
        try:
            query = {"ball_id":ball_id}
            cursor = self.chunk_collection.find(query)
            cs = []
            async for chunk in cursor:
                chunk["_id"]= str(chunk["_id"])
                cs.append(chunk)
            return Ok(cs)
        except Exception as e:
            return Err(e)
    async def find_one_ball(self,query:Dict[str, Any]={}):
        try:
            found_user = await self.chunk_collection.find_one(query)
            return Ok(found_user)
        except Exception as e:
            return Err(e)
    async def create(self,chunk:ModelX.ChunkModel,by_alias:bool=True)->Result[InsertOneResult,Exception]:
        try:
            chunk_data = chunk.model_dump(by_alias=by_alias)
            result    = await self.chunk_collection.insert_one(chunk_data)
            return Ok(result)
        except Exception as e:
            return Err(e)