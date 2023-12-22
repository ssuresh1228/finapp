from fastapi_users import schemas
from pydantic import Field
from datetime import datetime
from beanie import Document, PydanticObjectId

class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str = Field(...)
    full_name: str = Field(...)
    phone: str = Field(...)
    password_hash: str = Field(...)

'''
classes below are for validation/serialization - don't actually interact with DB
'''

# BaseUser: basic fields + validation (ID, email, is_active, is_verified, is_superuser) 
class UserRead(schemas.BaseUser[PydanticObjectId]):
    username: str = Field(...)
    full_name: str = Field(...)
    phone: str = Field(...)

# BaseCreateUser: handles user registration - mandatory email + password fields
class NewUser(schemas.BaseUserCreate[PydanticObjectId]):
    username: str = Field(...)
    full_name: str = Field(...)
    phone: str = Field(...)

# BaseUpdateUser: handles updating user profiles (optional password field)
class NewUser(schemas.BaseUserCreate[PydanticObjectId]):
    username: str = Field(...)
    full_name: str = Field(...)
    phone: str = Field(...)