from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from axobackend.controllers import auth, axoobjects, axoshadows, virtual_environments, endpoints, tasks, results, code
import axobackend.db as DbX

from dotenv import load_dotenv
import os 

@asynccontextmanager
async def lifespan(app: FastAPI):

    ENV_FILE = os.environ.get("ENV_FILE","")
    if ENV_FILE != "" and os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
    await DbX.connect_to_mongo()
    yield 
    await DbX.close_mongo_connection()

    

app = FastAPI(
    lifespan= lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"], # Frontend URL
    allow_credentials = False,
    allow_methods     = ["*"], # Allow all methods (POST, GET, etc.)
    allow_headers     = ["*"], # Allow all headers
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Axo API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth.auth_router)


app.include_router(virtual_environments.environments_router)
app.include_router(endpoints.endpoints_router)
app.include_router(axoobjects.axo_router)
app.include_router(axoshadows.axos_router)
app.include_router(tasks.tasks_router)
app.include_router(results.results_router)

app.include_router(code.code_router)