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
from server.util.auth_backend import generate_verification_token, generate_password_reset_token, generate_session_token
import secrets
from server.util.auth_backend import redis
from server.schemas.email_schema import EmailSchema

# core logic of user management
# ID Parser Mixin: ObjectIDIDMixin + PydanticObjectId used for MongoDB's ObjectID
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
   
    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Request] = None):
        #TODO: reports/transactions functionality 
        # redis token is valid for 1 hour
        session_key = await generate_session_token(str(user.id))
        print("\n-----\nSERVER LOG:", f"user {user.id} logged in")
        
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # /register handler - creates token and sends email for user verification
        #verification token and construct the verification URL
        verify_token = await generate_verification_token(str(user.id))
        verification_url = f"http://localhost:8000/auth/verify?verify_token={verify_token}"
        email = EmailSchema(email_addresses = [user.email])
        print("\n-----\nSERVER LOG:",  f"User {user.fullname} registered - verification token: {verify_token}.")
        await email_utils.send_verification_email(email, verification_url)
        
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        # /verify handler: user is rerouted to frontend, this is just for logging   
        print("\n-----\nSERVER LOG:", f"user {user.id} verified\n-----")
    
    async def validate_new_user_password(self, password: str, user: Union[UserCreate, User]) -> None:
        if len(password) < 5:
            raise InvalidPasswordException(reason = "Password must be at least 5 characters")
        if user.email in password:
            raise InvalidPasswordException(reason = "Password cannot contain an email address")
        if user.phone_number in password:
            raise InvalidPasswordException(reason = "Password cannot contain a phone number")
        if user.fullname in password:
            raise InvalidPasswordException(reason = "Password cannot contain a name")
    
    async def validate_reset_password(self, new_password: str) -> None:
        if len(new_password) < 5:
            raise InvalidPasswordException("Password must be longer than 5 characters.")       
    
    async def on_after_forgot_password(self, user: User, request: Optional[Request] = None):
        reset_token = await generate_password_reset_token(str(user.id))
        await redis.set(f"password_reset:{reset_token}", str(user.id))
        reset_url = f"http://localhost:8000/reset-password?reset_token={reset_token}"
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_reset_email(email, reset_url)
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. \nReset token: {reset_token}\n-----")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_change_confirmation(email)
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