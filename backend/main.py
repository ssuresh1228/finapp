from fastapi import FastAPI, APIRouter 
from beanie import init_beanie
from server.model.user_model import User, UserCreate
from server.model.report_model import Report
from server.database import db
from pydantic import BaseModel
from server.routers import user_route

app = FastAPI()

@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message" : "root endpoint: this is the main entrypoint to the rest of the app"}

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
app.include_router(user_route.router)