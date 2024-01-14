from beanie import Document
from pydantic import BaseModel
from fastapi_users.db import BeanieBaseUser
<<<<<<< HEAD
from datetime import datetime, timedelta
=======
>>>>>>> main

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
    hashed_password: str
<<<<<<< HEAD

# used for local caching 
class Settings: 
    use_cache=True
    cache_expiration_time = timedelta(seconds=10)
    cache_capacity = 5 # max queries to cache

=======
    
>>>>>>> main
class Config:
    schema_example = {
        "user example": {
            "email" : "user@example.com",
            "fullname": "firstname lastname",
            "username": "user123",
            "phone_number":"123-456-7890",
            "hashed_password": "hashedpassword123"
        }
    }