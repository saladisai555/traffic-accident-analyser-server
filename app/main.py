from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
import re
import inspect
from app.startup import lifespan
from app.routes import auth, predict, dashboard, weather
from app.config import settings

app = FastAPI(
    title="Traffic Accident Analyser",
    description="API for traffic accident prediction and analysis",
    version="0.1.0",
    lifespan=lifespan,
)

security = HTTPBearer()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Traffic Accident Analyser",
        version="0.1.0",
        description="API for traffic accident prediction and analysis with JWT authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            if (
                re.search(r"get_current_user", inspect.getsource(endpoint)) or
                re.search(r"Depends\(get_current_user\)", inspect.getsource(endpoint))
            ):
                if path not in openapi_schema["paths"]:
                    continue
                if method not in openapi_schema["paths"][path]:
                    continue
                    
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "BearerAuth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(weather.router)


@app.get("/")
async def root():
    return {
        "message": "Traffic Accident Analyser API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
