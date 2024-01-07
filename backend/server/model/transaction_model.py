from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field

class Transaction(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    userID: Link[User]
    amount: condecimal(decimal_places = 2)

# transaction category definition - embedded model
class Category(BaseModel):
   id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
   name: str = Field(...)
   description: str = Field(...)