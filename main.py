import uvicorn
from fastapi import FastAPI
from database import engine
from models.user import Users
from config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from routers import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Users.metadata.create_all(bind=engine)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
