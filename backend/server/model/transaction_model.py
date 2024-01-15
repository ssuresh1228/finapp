from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field

# nested in transaction model
class Category(BaseModel):
   #id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
   #this is for testing
   id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
   name: List[str] # to handle multiple categories in a transaction
   description: str = Field(...)
  
class Transaction(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    userID: PydanticObjectId
    amount: pydecimal128
    creation_date: datetime
    categories: List[Category]
    
