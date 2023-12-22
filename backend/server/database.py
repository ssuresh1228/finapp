import motor
import motor.motor_asyncio
from model.report_model import Report
from model.transaction_model import Transaction
from model.user_model import User

from beanie import init_beanie

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient("your_db_link_here")
    await init_beanie(database=client.db_name, document_models=[Report, Transaction, User])