from fastapi_users.db import BeanieUserDatabase
from .model.user_model import User
from fastapi import Depends

async def get_user_db():
    yield BeanieUserDatabase(User)

async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    # Local import to avoid circular dependency
    from server.util.user_manager import UserManager
    yield UserManager(user_db)

async def get_transaction_manager():
    # Local import to avoid circular dependency
    from server.util.transaction_manager import TransactionManager
    yield TransactionManager()
    
async def get_email_manager():
    from server.util.email_manager import EmailManager
    yield EmailManager()

async def get_auth_manager():
    from server.util.auth_manager import AuthManager
    yield AuthManager()