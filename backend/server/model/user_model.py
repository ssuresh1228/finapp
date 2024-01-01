from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

# create user model 
class User(BeanieBaseUser, Document):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

# user validation model - makes sure all fields are present before actually creating a user (validate_password)
class UserCreate(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str