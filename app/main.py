
from fastapi import FastAPI
from app.api import api_router
from .settings import settings

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
    )

    app.include_router(
        api_router,
        # prefix=settings.API_PREFIX,
    )

    return app

app = get_application()

@app.get("/")
async def read_root():
    return {"message": "Guardium AI Registry Service is running!"}
