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
from server.util import email_utils
from server.util.auth_backend import generate_verification_token
import secrets
from server.util.auth_backend import redis
from server.schemas.email_schema import EmailSchema

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

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} requested verification. Verification token: {token}\n-----")
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_verification_email(email, token)
      
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # called after successful user registration (user still needs to be verified)
        # sends a generic welcome email with a link for verification
        email = EmailSchema(email_addresses = [user.email])
        print("\n-----\nSERVER LOG:",  f"User {user.fullname} created an account - verification required.")
        await email_utils.send_user_welcome(email) 
        
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        # what to do immediately after successful user verification: sends verification confirmation email
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_user_verified_confirmation(email)    
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
        email = EmailSchema(email_addresses = [user.email])
        await send_password_reset_email(email, token)
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. Reset token: {token}\n-----")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        email = EmailSchema(email_addresses = [user.email], body = email.body)
        await send_password_change_confirmation(email)
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