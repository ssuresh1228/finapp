from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from user_model import User
from datetime import date, datetime
from typing import List

# report options defined in embedded models
class Report(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    UserID: Link[User]
    report_type: str
    generated_on: Datetime.now() 


'''
!!!airflow is responsible for populating embedded models!!!
'''
# aggregation of transformed data from all other embedded models
class Data(BaseModel):
    category_breakdown: List[CategoryBreakdown]
    avg_transaction: condecimal(decimal_places = 2) = Decimal('0.00')
    total_expenses: condecimal(decimal_places = 2) = Decimal('0.00')
    total_income: condecimal(decimal_places = 2) = Decimal('0.00')
    start_date: date
    end_date: date

# amount spent per category
class CategoryBreakdown(BaseModel):
    category_id: str
    total_amount: condecimal(decimal_places = 2) = Decimal('0.00')
    
# average transaction amount (income/expenses) over defined time period
class AvgTransactionAmount(BaseModel):
    transaction_type: str
    start_date: date
    end_date: date
    avg_transaction: condecimal(decimal_places = 2) = Decimal('0.00')

# total expenses over defined time period
class TotalExpenses(BaseModel):
    start_date: date
    end_date: date
    avg_transaction: condecimal(decimal_places = 2) = Decimal('0.00')

# total income over defined time period
class TotalIncome(BaseModel):
    start_date: date
    end_date: date
    avg_transaction: condecimal(decimal_places = 2) = Decimal('0.00')