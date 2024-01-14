from beanie import PydanticObjectId 
from pydantic import BaseModel, EmailStr
from fastapi_users import schemas

# used when a new user is registered
# password field: plaintext is used here, needs to be hashed
class UserCreate(schemas.BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

# defines how data is sent back in responses
# used for displaying in frontend
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
    hashed_password: str
    
class UserLoginRequest(BaseModel):
    entered_email: EmailStr 
    entered_password: str

class UserRegistrationRequest(BaseModel):
    email: str
    fullname: str
    username: str
    phone_number: str
    password: str