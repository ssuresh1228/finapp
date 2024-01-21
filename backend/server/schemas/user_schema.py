from beanie import PydanticObjectId 
from pydantic import BaseModel, EmailStr
from fastapi_users import schemas


class UserCreateValidator(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str

# defines how data is sent back in responses
# used for displaying in frontend
class UserReadValidator(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str

# used when an existing user updates their info
class UserUpdateValidator(BaseModel):
    email: str
    fullname: str
    username: str 
    phone_number: str
    hashed_password: str
    
class UserLoginValidator(BaseModel):
    email: EmailStr 
    password: str

class UserRegistrationValidator(BaseModel):
    email: str
    fullname: str
    username: str
    phone_number: str
    hashed_password: str
    
class UserEmailValidator(BaseModel):
    email: str
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    new_password:str
    confirm_password:str
    reset_token: str

class VerificationRequest(BaseModel):
    verify_token: str