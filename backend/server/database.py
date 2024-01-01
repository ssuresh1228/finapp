import motor.motor_asyncio
from beanie import Document
from .model.user_model import User
from fastapi_users.db import BeanieUserDatabase

# setup db connection
DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["finapp-db"]

# db adapter: links db config and users logic
async def get_user_db():
    yield BeanieUserDatabase(User)