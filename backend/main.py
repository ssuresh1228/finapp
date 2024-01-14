from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware 
from beanie import init_beanie
from server.model.user_model import User, UserCreate
from server.model.report_model import Report
from server.model.transaction_model import Transaction
from server.database import db
from pydantic import BaseModel
from server.routers import auth_router, transaction_router

app = FastAPI()
router = APIRouter()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
            Transaction
        ],
    )

# user registration, verification, forgot password, reset password
app.include_router(
    auth_router.custom_auth_router,
    prefix = "/auth",
    tags = ["auth"]
)

app.include_router(
    transaction_router.router,
    tags = ["transaction"]
)