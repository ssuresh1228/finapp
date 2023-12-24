from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase

#core logic for fastapi-users
# create user model (fastapi users)
# id and email handled by default 
class User(BeanieBaseUser, Document):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

# db adapter: links db config and users logic
async def get_user_db():
    yield BeanieUserDatabase(User)
    
# user validation model
class CreateUserRequest(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str