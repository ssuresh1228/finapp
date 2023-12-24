from fastapi import FastAPI 
from beanie import init_beanie
from server.model.user_model import User
from server.database import db
from pydantic import BaseModel

app = FastAPI()

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
class CreateUserRequest(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

@app.post("/register")
async def create_user(user_data: CreateUserRequest):
    user = User(email=user_data.email, 
                fullname=user_data.fullname, 
                username=user_data.username, 
                phone_number=user_data.phone_number, 
                hashed_password=user_data.hashed_password)
    await user.insert()
    return {"message": "User created successfully", "user": user}