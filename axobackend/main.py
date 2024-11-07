from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from axobackend.routers import auth, virtual_environments, endpoints, axo, axos, tasks, results, code


app = FastAPI()

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
app.include_router(axo.axo_router)
app.include_router(axos.axos_router)
app.include_router(tasks.tasks_router)
app.include_router(results.results_router)
app.include_router(code.code_router)