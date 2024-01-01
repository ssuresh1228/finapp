from fastapi import FastAPI, APIRouter 
from fastapi_users import FastAPIUsers
from beanie import init_beanie
from server.model.user_model import User
from server.model.report_model import Report
from server.database import db
from pydantic import BaseModel
from server.routers import user_router, auth_router

app = FastAPI()
router = APIRouter()

@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message" : "root endpoint: entrypoint to the rest of the app"}

# initialize beanie to discover models
# add models here
@app.on_event("startup")
async def beanie_startup():
    await init_beanie(
        database=db,
        document_models= [
            User,
            Report,
        ],
    )

# register routers here
app.include_router(
    auth_router.auth_router,
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    auth_router.registration_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    auth_router.verification_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    auth_router.reset_password_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(user_router.router)
