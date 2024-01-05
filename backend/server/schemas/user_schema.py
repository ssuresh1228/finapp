from beanie import PydanticObjectId 
from pydantic import BaseModel, EmailStr
from fastapi_users import schemas

# used when a new user is registered
# password field: plaintext is used here, needs to be hashed
class UserCreate(schemas.BaseUserCreate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str

# used to define how data is sent back in responses
# this schema is what's used for the frontend
class UserRead(schemas.BaseUser[PydanticObjectId]):
    email: str
    fullname: str
    username: str 
    phone_number: str

# used when an existing user updates their info
class UserUpdate(schemas.BaseUserUpdate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str
    
class UserLoginRequest(BaseModel):
    user_email: EmailStr 
    user_password: str

class UserRegistrationRequest(BaseModel):
    email: str
    fullname: str
    username: str
    phone_number: str
    password: str