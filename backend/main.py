from fastapi import FastAPI, APIRouter 
from beanie import init_beanie
from server.model.user_model import User, CreateUserRequest
from server.database import db
from pydantic import BaseModel
from server.routers import user_route

app = FastAPI()
router = APIRouter()

@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message" : "root endpoint: this is the main entrypoint to the rest of the app"}

# initialize beanie to discover models
@app.on_event("startup")
async def beanie_startup():
    await init_beanie(
        database=db,
        document_models= [
            User,
        ],
    )

# register routes here
app.include_router(user_route.router)