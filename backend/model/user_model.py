from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field

# defines user collection
class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str
    email: str
    passwordHash: str 

# defines user's profile info
# embedded model in user collection 
class ProfileInfo(BaseModel):
    FullName: str
    PhoneNumber: str 
    DateOfBirth: datetime      