from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, ValidationError
from fastapi import FastAPI
from typing import List, Union, Optional
from decimal import Decimal
from server.util.types.PyDecimal128 import PyDecimal128 as pydecimal128
from typing_extensions import Annotated
from datetime import date as date_type, datetime

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
    
