from beanie import Document
from pydantic import BaseModel
from fastapi_users.db import BeanieBaseUser

# create user model 
class User(BeanieBaseUser, Document):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

# user validation model
class UserCreate(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str
    
class Config:
    schema_example = {
        "user example": {
            "email" : "user@example.com",
            "fullname": "firstname lastname",
            "username": "user123",
            "phone_number":"123-456-7890",
            "password": "hashedpassword123"
        }
    }