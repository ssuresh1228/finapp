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
import server.util.email_utils
from server.util.auth_backend import generate_verification_token
import secrets
from server.util.auth_backend import redis

PASSWORD_RESET_SECRET = secrets.token_urlsafe(32)
VERIFICATION_TOKEN_SECRET = secrets.token_urlsafe(32)

# core logic of user management
# ID Parser Mixin: ObjectIDIDMixin + PydanticObjectId used for MongoDB's ObjectID
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    
    # keep secrets consistent so earlier users aren't invalidated
    # JWTs are auto-generated for password reset emails -signed by reset_password_token
    reset_password_token_secret = PASSWORD_RESET_SECRET
    verification_token_secret = VERIFICATION_TOKEN_SECRET
    
    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Request] = None):
        #TODO: reports/transactions functionality
        # redis token is valid for 1 hour
        await redis.set(redis_token, str(user.id), ex=3600)
        print("\n-----\nSERVER LOG:", f"user {user.id} logged in")

    async def on_after_request_verify(self, user: User, regen_redis_token: str, request: Optional[Request] = None):
        # handles /request-verify-token endpoint
        # sends user the verification_token_secret to their email (they'll use it for /verify)
        # creating another redis token in case user needs another verification
        regen_redis_token = generate_verification_token()
        await send_verification_email(user.email, regen_redis_token)
        print("\n-----\nSERVER LOG:", f"user {user.id} requested verification. Verification token: {regen_redis_token}\n-----")
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # creates an unverified user - reqiuires verification
        print("\n-----\nSERVER LOG:",  f"User {user.fullname} created an account - verification required.")
        redis_token = generate_verification_token()
        await send_verification_email(user.email) 
        
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        # what to do immediately after successful user verification
        # updates their status to verified
        #TODO: test verification email
        await send_user_verified_confirmation(user.email)        
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
        #TODO: test sending reset password email
        await send_password_reset_email(user.email, token)
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. Reset token: {token}\n-----")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        #TODO: test user email confirming password change
        await send_password_change_confirmation(user.email)
        print("\n-----\nSERVER LOG:")  
        print(f"user {user.id} successfully reset their password\n-----")
    
    async def on_after_update(self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"User {user.id} updated: {update_dict}\n-----")
    
    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} is going to be deleted\n-----")
        
    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} successfully deleted\n-----")
    
# UserManager is injected at runtime: get_user_db injects the fastapi-users database instance 
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)