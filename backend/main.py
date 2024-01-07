from fastapi import FastAPI, APIRouter 
from fastapi_users import FastAPIUsers
from beanie import init_beanie
from server.model.user_model import User
from server.model.report_model import Report
from server.database import db
from pydantic import BaseModel
from server.routers import auth_router

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

# user registration, verification, forgot password, reset password
app.include_router(
    auth_router.custom_auth_router,
    prefix = "/auth",
    tags = ["auth"]
)
