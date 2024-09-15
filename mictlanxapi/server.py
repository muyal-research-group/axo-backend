from fastapi import FastAPI, HTTPException, Depends,Response,status,Query
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from typing import Annotated
import random
from mictlanxapi.models import UserModel,CredentialsModel,AuthenticationAttemptModel
import mictlanxapi.models as ModelX
import mictlanxapi.repositories as RepositoryX
from bson import ObjectId
from mictlanxapi.security import hash_value,verify_password,create_access_token
from jwt.exceptions import InvalidTokenError
from mictlanxapi.dto import UserDTO
from fastapi.middleware.cors import CORSMiddleware

# from typing import List

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MongoDB setup
# MONGO_DETAILS = "mongodb://localhost:27017"
MONGO_DETAILS = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client        = AsyncIOMotorClient(MONGO_DETAILS)
db            = client.my_database  # Replace 'my_database' with your database name

# Collections
user_collection                   = db.get_collection("users")
credentials_collection            = db.get_collection("credentials")
authentication_attempt_collection = db.get_collection("authentitcation_attempt")
bucket_collection                 = db.get_collection("buckets")
bucket_info_collection            = db.get_collection("buckets_info")
group_collection                  = db.get_collection("groups")
group_user_collection             = db.get_collection("groups_users")
ball_collection                   = db.get_collection("balls")
chunk_collection                   = db.get_collection("chunks")

credentials_respository = RepositoryX.CredentialsRepository(
    client=client,
    collection= credentials_collection
)
user_repository   = RepositoryX.UserRepository(
    client=client,
    collection= user_collection
)
bucket_repository = RepositoryX.BucketRepository(
    client                 = client,
    bucket_collection      = bucket_collection,
    bucket_info_collection = bucket_info_collection
)
group_repository = RepositoryX.GroupRepository(
    client                = client,
    group_collection      = group_collection,
    group_user_collection = group_user_collection
)
ball_repository = RepositoryX.BallRepository(
    client=client,
    ball_collection=ball_collection
)
chunk_repository = RepositoryX.ChunkRepository(
    client=client,
    chunk_collection=chunk_collection
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
    print("DATA", data)
    user = UserDTO(**data, user_id= str(data["_id"]))
    print("USER", user)
    print("USER_ID", user.user_id)
    # get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user






@app.post("/credentials/")
async def create_credentials(credentials: CredentialsModel):
    # print("credentials", credentials)
    query = {
        "$or":[{"_id":ObjectId(credentials.user_id)}]
    }
    # found_user = await user_collection.find_one(query)
    found_user_result = await user_repository.find_one(query=query)
    if found_user_result.is_err:
        raise HTTPException(detail=str(found_user_result.unwrap_err()), status_code=500)
    
    found_user = found_user_result.unwrap()
    
    if not found_user:
        raise HTTPException(status_code=404, detail="User not found.")
    result = await credentials_respository.create(
        credentials=credentials,
    )
    if result.is_err:
        raise HTTPException(detail=str(result.unwrap_err()), status_code=500)

    # credentials_dict = credentials.model_dump()
    # credentials_dict["password"] = await hash_value(credentials_dict.get("password",""))
    # credentials_dict["pin"] = await hash_value(credentials_dict.get("pin",""))
    # credentials_dict["token"] = await hash_value(credentials_dict.get("token",""))
    # await credentials_collection.insert_one(credentials_dict)
    return Response(content=None, status_code=201)

@app.post("/users/")
async def create_user(user: UserModel):
    query = {
        "$or":[{"username":user.username},{"email":user.email}]
    }
    found_user_result = await user_repository.find_one(
        query= query
    )
    if found_user_result.is_err:
        raise HTTPException(detail=str(found_user_result.unwrap_err()), status_code=500 )
    found_user = found_user_result.unwrap()
    if found_user:
        raise HTTPException(status_code=501, detail="User already exists.")
    user_dict_result = await user_repository.create(
        user=user,
    )
    if user_dict_result.is_err:
        raise HTTPException(detail=str(user_dict_result.unwrap()), status_code=500)
    user_dict = user.model_dump(by_alias=True)
    user_dict["_id"] = str(user_dict["_id"])
    return user_dict



@app.post("/auth")
async def authenticate(authentication_attemp:AuthenticationAttemptModel):
    query = {
        "$or": [{"username":authentication_attemp.username }]
    }
    found_user = await user_collection.find_one(query)
    if not found_user:
        detail="Incorrect username or password."
        raise HTTPException(status_code=404, detail=detail)
    user_id                        = str(found_user["_id"])
    credentials                    = await credentials_collection.find_one({"user_id": user_id  })
    verified                       = await verify_password(stored_value= credentials.get("password",''), provided_value=authentication_attemp.password)
    authentication_attemp.password = await hash_value(value=authentication_attemp.password)
    # ________________________________________________________________________________________
    if verified:
        authentication_attemp.status = 1
        result = authentication_attempt_collection.insert_one(authentication_attemp.model_dump())
        found_user["_id"] = str(found_user["_id"])
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            SECRET_KEY=SECRET_KEY,
            ALGORITHM=ALGORITHM,
            data={
                    "sub": user_id
            },
            expires_delta=access_token_expires
        )
        found_user["token"] = access_token
        first = found_user["first_name"]
        last = found_user["last_name"]
        found_user["initials"] = "{}{}".format(first[0], last[0] ).upper()
        found_user["fullname"] = "{} {}".format(first,last).lower().title()
        return found_user
    # ________________________________________________________________________________________
    authentication_attemp.status = -1
    authentication_attempt_collection.insert_one(authentication_attemp.model_dump())
    raise HTTPException(
        status_code=501,
        detail="Incorrect username or password."
    )

@app.post("/validate-token")
async def validate_token(
    current_user: Annotated[UserDTO, Depends(get_current_active_user)],
):
    return Response(content=None, status_code=204)




@app.post("/buckets")
async def create_bucket(bucket:ModelX.BucketModel):
    # try:
    query = {
        "$or": [{"_id":ObjectId(bucket.user_id) }]
    }
    found_user = await user_collection.find_one(query)
    if not found_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    found_bucket_result = await bucket_repository.find_one_bucket_by_alias(alias=bucket.alias)
    if found_bucket_result.is_err:
        raise HTTPException(status_code=500, detail=str(found_bucket_result.unwrap_err()))
    found_bucket = found_bucket_result.unwrap()
    print("FOUND_BUCKET", found_bucket)
    if found_bucket:
        raise HTTPException(status_code=403,detail="Bucket alias already exists.")

    first_name:str = found_user.get("first_name","GROUP")
    random_integer = random.randint(0, 1000)
    group = ModelX.GroupModel(
        alias="{}_{}".format(first_name.upper(),  random_integer)
    )
    result = await group_repository.create(
        user_id=str(bucket.user_id),
        group= group,
    )
    result = await bucket_repository.create(bucket=bucket,group_id=str(group.group_id))
    return Response(content=None, status_code=201)


@app.get("/buckets")
async def get_buckets(
    current_user: Annotated[UserDTO, Depends(get_current_active_user)],
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return (max: 100)")
):
    buckets_result =await bucket_repository.find_buckets_and_infos_all(
        {
            "user_id": str(current_user.user_id)
        },
        skip=skip,
        limit=limit
    )
    if buckets_result.is_err:
        raise HTTPException(detail=str(buckets_result.unwrap_err()), status_code=500)
    buckets_cursor = buckets_result.unwrap()

    return buckets_cursor

@app.post("/balls")
async def create_ball(ball:ModelX.BallModel):
    query = {
        "$or": [{"_id":ObjectId(ball.bucket_id) }]
    }

    found_bucket_result = await bucket_repository.find_one_bucket(query=query)
    if found_bucket_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_one_bucket: {}".format(ball.bucket_id))
    
    found_bucket = found_bucket_result.unwrap()
    if not found_bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    result = await ball_repository.create(
        ball=ball,
    )
    if result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong creating the ball: {}".format(ball.ball_id))
    
    return Response(content=None, status_code=204)
 
@app.post("/chunks")
async def create_chunk(chunk:ModelX.ChunkModel):
    query = {
        "$or": [{"_id":ObjectId(chunk.ball_id) }]
    }

    found_ball_result = await ball_repository.find_one_ball(query=query)

    if found_ball_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_one_ball: {}".format(chunk.bucket_id))
    
    found_ball = found_ball_result.unwrap()
    if not found_ball:
        raise HTTPException(status_code=404, detail="Ball not found.")
    result = await chunk_repository.create(
        chunk= chunk
    )
    if result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong creating the chunk: {}".format(chunk.chunk_id))
    
    return Response(content=None, status_code=204)


@app.get("/buckets/{bucket_id}/balls")
async def get_balls(
    bucket_id:str,
    current_user: Annotated[UserDTO, Depends(get_current_active_user)],
):
    query = {
        "$or": [{"_id":ObjectId(bucket_id) }]
    }

    found_bucket_result = await bucket_repository.find_one_bucket(query=query)
    if found_bucket_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_one_bucket: {}".format(bucket_id))
    
    found_bucket = found_bucket_result.unwrap()
    if not found_bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    balls_result = await ball_repository.find_balls_by_bucket_id(bucket_id=bucket_id)
    if balls_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong getting the balls.")
    balls = balls_result.unwrap()
    return balls

    # bucket_id
    
@app.get("/buckets/{bucket_id}/{ball_id}/chunks")
async def get_chunks(
    bucket_id:str,
    ball_id:str,
    current_user: Annotated[UserDTO, Depends(get_current_active_user)],
):
    query = {
        "$or": [{"_id":ObjectId(bucket_id) }]
    }

    found_bucket_result = await bucket_repository.find_one_bucket(query=query)
    if found_bucket_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_one_bucket: {}".format(bucket_id))
    
    found_bucket = found_bucket_result.unwrap()
    if not found_bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    
    found_ball_result = await ball_repository.find_by_ball_id(ball_id=ball_id)
    if found_ball_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_ball_by_id: {}".format(ball_id))
    found_ball = found_ball_result.unwrap()
    if not found_ball:
        raise HTTPException(status_code=404, detail="Ball not found.")
    
    chunks_result = await chunk_repository.find_chunks_by_ball_id(ball_id=ball_id)
    if chunks_result.is_err:
        raise HTTPException(status_code=500, detail="Something went wrong find_chunks_by_ball_id: {}".format(ball_id))
    chunks = chunks_result.unwrap()

    return chunks
    # buckets_result =await chunk_repository.find_chunks_by_ball_id(
    #     {
    #         "ball_id": str(current_user.user_id)
    #     },
    # )
    # if buckets_result.is_err:
    #     raise HTTPException(detail=str(buckets_result.unwrap_err()), status_code=500)
    # buckets_cursor = buckets_result.unwrap()

    # return buckets_cursor