from beanie import PydanticObjectId
from fastapi_users import schemas

# CRUD operations for users implemented here
class UserCreate(schemas.BaseUserCreate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

class UserRead(schemas.BaseUser[PydanticObjectId]):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

class UserUpdate(schemas.BaseUserUpdate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str