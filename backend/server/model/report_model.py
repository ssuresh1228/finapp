from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field, PastDate
from .user_model import User
from datetime import datetime
from typing import List, Annotated
from decimal import Decimal

# report options defined in embedded models
class Report(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    UserID: Annotated[Link[User], "links report to its user"]
    report_type: Annotated[str, "type of report generated"]
    generated_on: Annotated[datetime, "when report was generated"] = Field(default = datetime.now())

# amount spent per category
class CategoryBreakdown(BaseModel):
    category_id: str = Field(default = "none", min_length = 3)
    total_amount: Annotated[Decimal, "total amount spent in specified category"]
    
# average income over defined time period
# PastDate: validation constraint enforcing start_date's value must be in the past
class AverageIncome(BaseModel):
    start_date: Annotated[PastDate, "avg income: starting date"]
    end_date: Annotated[datetime, "avg income: starting date"]
    avg_income: Annotated[Decimal, "start_date to end_date: avg income value"] = Field(default = 0.00, decimal_places=2)
    
# average expenses over defined time period
class AverageExpenses(BaseModel):
    start_date: Annotated[PastDate, "avg expenses: starting date"]
    end_date: Annotated[datetime, "avg expenses: starting date"]
    avg_expense: Annotated[Decimal, "start_date to end_date: avg expense value"] = Field(default = 0.00, decimal_places=2)

# total expenses over defined time period
class TotalExpenses(BaseModel):
    start_date: Annotated[datetime, "total expenses: starting date"]
    end_date: Annotated[datetime, "total expenses: starting date"]
    total_expenses: Annotated[Decimal, "start_date to end_date: total expenses"] = Field(default = 0.00, decimal_places=2)

# total income over defined time period
class TotalIncome(BaseModel):
    start_date: Annotated[PastDate, "total income: starting date"]
    end_date: Annotated[datetime, "total income: ending date"]
    avg_transaction: Annotated[Decimal, "start_date to end_date: avg transaction value"] = Field(default = 0.00, decimal_places=2)
    
# aggregation of transformed data from all other embedded models above
class Data(BaseModel):
    category_breakdown: Annotated[List[CategoryBreakdown], "list of categories"]
    average_income: Annotated[Decimal, "average income from AverageIncome model"] = Field(default = 0.00, decimal_places=2)
    average_expenses: Annotated[Decimal, "average expenses from AverageExpenses model"] = Field(default = 0.00, decimal_places=2)
    total_expenses: Annotated[Decimal, "total expenses from TotalExpenses model"] = Field(default = 0.00, decimal_places=2)
    total_income: Annotated[Decimal, "total income from TotalIncome model"] = Field(default = 0.00, decimal_places=2)
    start_date: Annotated[PastDate, "start date of associated report"]
    end_date: Annotated[datetime, "end date of associated report"]