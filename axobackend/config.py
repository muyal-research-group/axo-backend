import os
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient

SECRET_KEY                        = os.environ.get("SECRET_KEY","09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM                         = os.environ.get("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES       = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES","30"))
oauth2_scheme                     = OAuth2PasswordBearer(tokenUrl="token")
MONGO_DETAILS                     = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client                            = AsyncIOMotorClient(MONGO_DETAILS)
db                                = client.axo
user_collection                   = db.get_collection("users")
credentials_collection            = db.get_collection("credentials")
authentication_attempt_collection = db.get_collection("authentitcation_attempt")
envs_collection                   = db.get_collection("virtual_environments")
endpoint_collection               = db.get_collection("endpoints")
axo_object_collection             = db.get_collection("axo_objects")
axos_collection                   = db.get_collection("axos")
tasks_collection                  = db.get_collection("tasks")
results_collection                = db.get_collection("results")
code_collection                   = db.get_collection("code")

