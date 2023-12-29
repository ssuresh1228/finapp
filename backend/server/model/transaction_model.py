from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from user_model import user
from decimal import Decimal

class Transaction(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    userID: Link[User]
    amount: condecimal(decimal_places = 2)

# transaction category definition - embedded model
class Category(BaseModel):
   id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
   name: str
   description: str 