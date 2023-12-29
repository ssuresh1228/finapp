from beanie import PydanticObjectId
from fastapi_users import schemas

"""fast-api users default fields:
    id (ID) – user's Unique identifier. matches the type of ID defined (PydanticObjectID)
    email (str) – user's email. validated by email-validator.
    is_active (bool) – if user is active. If not, login and forgot password requests will be denied. Defaults to True.
    is_verified (bool) – if user is verified. Optional but helpful with the verify router logic. Defaults to False.
    is_superuser (bool) – if user is a superuser. Useful to implement administration logic. Defaults to False.
"""

# used when a new user is registered
# password field: plaintext is used here, needs to be hashed
class UserCreate(schemas.BaseUserCreate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str

# used to define how data is sent back in responses
class UserRead(schemas.BaseUser[PydanticObjectId]):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str

# used when an existing user updates their info
class UserUpdate(schemas.BaseUserUpdate):
    email: str
    fullname: str
    username: str 
    phone_number: str
    password: str