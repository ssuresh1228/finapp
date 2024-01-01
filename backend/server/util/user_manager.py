from server.model.user_model import User, UserCreate
from server.database import get_user_db
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi_users_db_beanie import ObjectIDIDMixin 
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from typing import Optional, Union, Dict, Any
from beanie import PydanticObjectId
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.responses import JSONResponse
from server.util.email_utils import send_verification_email
from server.util.auth_backend import generate_verification_token
import secrets
from server.util.auth_backend import redis
from server.util.redis import test_redis

PASSWORD_RESET_SECRET = secrets.token_urlsafe(32)
VERIFICATION_TOKEN_SECRET = secrets.token_urlsafe(32)

# UserManager class: core logic of user management
# ID Parser Mixin: ObjectIDIDMixin + PydanticObjectId used for MongoDB's ObjectID
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    
    # keep consistent so earlier tokens aren't invalidated
    reset_password_token_secret = PASSWORD_RESET_SECRET
    verification_token_secret = VERIFICATION_TOKEN_SECRET
    
    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Request] = None):
        #TODO: depends on reports/transactions 
        print("\n-----\nSERVER LOG:", f"user {user.id} logged in")

    async def on_after_request_verify(self, user: User, regen_redis_token: str, request: Optional[Request] = None):
        # handles /request-verify-token endpoint
        # sends user the verification_token_secret to their email (they'll use it for /verify)
        # creating another redis token in case user needs another verification
        regen_redis_token = generate_verification_token()
        await send_verification_email(user.email, regen_redis_token)
        print("\n-----\nSERVER LOG:", f"user {user.id} requested verification. Verification token: {regen_redis_token}\n-----")
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # creates an unverified user
        print("\n-----\nSERVER LOG:",  f"User {user.fullname} created an account - verification required.")
        print(f"Email: {user.email}")
        # await test_redis() # tests for redis connection
        # TODO: store token in Redis associated with user's ID
        redis_token = generate_verification_token()
        await redis.set(redis_token, str(user.id), ex=3600)
        await send_verification_email(user.email, redis_token) 
        
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        # what to do immediately after successful user verification
        # updates their status to verified        
        print("\n-----\nSERVER LOG:", f"user {user.id} verified\n-----")
    
    async def validate_password(self, password: str, user: Union[UserCreate, User]) -> None:
        if len(password) < 5:
            raise InvalidPasswordException(reason = "Password must be at least 5 characters")
        if user.email in password:
            raise InvalidPasswordException(reason = "Password cannot contain an email address")
        if user.phone_number in password:
            raise InvalidPasswordException(reason = "Password cannot contain a phone number")
        if user.fullname in password:
            raise InvalidPasswordException(reason = "Password cannot contain a name")
    
    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        #TODO: Jinja2 forgot_password template
        #TODO: send user reset_password_token_secret in email
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. Reset token: {token}\n-----")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:")  
        print(f"user {user.id} successfully reset their password\n-----")
    
    async def on_after_update(self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"User {user.id} updated: {update_dict}\n-----")
    
    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} is going to be deleted\n-----")
        
    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} successfully deleted\n-----")
    
# UserManager is injected at runtime: get_user_db is used here to inject the database instance 
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)