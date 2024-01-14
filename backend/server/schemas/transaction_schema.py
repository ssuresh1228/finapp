from beanie import PydanticObjectId
from pydantic import BaseModel, Field, ValidationError, validator
from decimal import Decimal
from typing_extensions import Annotated
from typing import List, Optional
from pydantic.functional_validators import field_validator
from datetime import date as date_type, timedelta
from server.util.types.PyDecimal128 import PyDecimal128 as pydecimal128

# pydantic schemas for endpoint validation/fetching
# validates incoming data before being handed down to the model layer for db

class CreateCategoryValidator(BaseModel):
    #id: PydanticObjectId
    name: List[str]
    description: str
    
class ReadCategoryValidator(BaseModel):
    #id: PydanticObjectId
    name: List[str]
    description: str
    
class UpdateCategoryValidator(BaseModel):
    #id: PydanticObjectId
    name: List[str]
    description: str
    
class DeleteCategoryValidator(BaseModel):
    #id: PydanticObjectId
    name: List[str]
    description: str

class CreateTransactionValidator(BaseModel):
    userID: PydanticObjectId
    amount: pydecimal128
    creation_date: date_type
    categories: List[CreateCategoryValidator] 
    @classmethod
    async def save_to_mongo(self):
        # Convert date to datetime for MongoDB
        self.creation_date = datetime.combine(self.creation_date, datetime.min.time())
        await self.save()
    
# includes pagination for frontend to use: loads 5 transactions/page
class ReadTransactionValidator(BaseModel):
    userID: PydanticObjectId
    page: int = 1
    page_size: int = 5
    amount:pydecimal128
    creation_date: date_type
    categories: List[ReadCategoryValidator]

class ReadTransactionDateRangeValidator(BaseModel):
    userID: PydanticObjectId
    page: int = 1
    page_size: int = 5
    amount:pydecimal128
    start_date: date_type
    end_date: date_type
    categories: List[ReadCategoryValidator] 

class DeleteTransactionValidator(BaseModel):
    transaction_ids: List[PydanticObjectId]
    userID: PydanticObjectId
    amount: pydecimal128
    creation_date: date_type
    categories: List[DeleteCategoryValidator] 
    
class UpdateTransactionValidator(BaseModel):
    id: PydanticObjectId
    userID: PydanticObjectId
    amount: pydecimal128
    creation_date: date_type
    categories: List[UpdateCategoryValidator]  
    
# used for updating multiple transactions at a time     
class BulkUpdateTransactionUpdateRequest(BaseModel):
    updates: List[UpdateTransactionValidator]