from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection
import os

client = None
# Get the MongoDB client and database instance
def get_database():
    global client
    # client                   = MongoClient(MONGODB_URI)
    MONGO_DATABASE_NAME      = os.environ.get("MONGO_DATABASE_NAME","axodb")
    return  client[MONGO_DATABASE_NAME] if client else None 

def get_collection(name:str)->AsyncIOMotorCollection:
    db =  get_database()
    return db[name] if not db is None else None 
# Startup event to initialize the MongoClient when the application starts
async def connect_to_mongo():
    global client
    MONGODB_URI = os.environ.get("MONGODB_URI","mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0")
    client = AsyncIOMotorClient(MONGODB_URI)

# Shutdown event to close the MongoClient when the application shuts down
async def close_mongo_connection():
    global client
    client.close()