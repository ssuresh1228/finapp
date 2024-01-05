from server.model.user_model import User, UserCreate
from server.database import get_user_db
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi_users.password import PasswordHelper
from fastapi_users_db_beanie import ObjectIDIDMixin 
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from typing import Optional, Union, Dict, Any
from beanie import PydanticObjectId, Document
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.responses import JSONResponse
from server.util import email_utils
from server.util.auth_utils import *
from server.schemas.email_schema import EmailSchema
from server.schemas.user_schema import *
from passlib.context import CryptContext

# helper method for user_login and registration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
async def verify_user_password(password: str, hashed_password: str):
    verified, _ = pwd_context.verify_and_update(password, hashed_password)
    return verified

# core logic of user management
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    
    async def check_user_exists(self, email: str):
        existing_user = await User.find_one(User.email == email)
        if existing_user: 
            raise ValueError("Error: user already exists, log in instead")
        return None
        
    async def save_new_user(self, user_data: User, request: Optional[Request] = None):
        # create a new user only if they don't exist in DB
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            return existing_user
        else:
            user = User(
                email = user_data.email,
                fullname = user_data.fullname,
                username = user_data.username,
                phone_number = user_data.phone_number,
                hashed_password = user_data.password
            )
            user.is_verified = True
            await user.save() 
            return user
    
    async def get_user_by_email(self, email:str, request: Optional[Request] = None):
        user = await User.find_one(User.email == email)
        return user
    
    async def user_login(self, email: str, password: str):
        # query db for this user
        user_in_db = await get_user_by_email(email)
        # return none if user doesn't exist 
        if not user_in_db:
            return None
        # compare hashed passwords to verify entered password
        if not await verify_user_password(password, user_in_db.hashed_password):
            # return None if not a match
            return None
        return user_in_db
   
    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Request] = None):
        #TODO: reports/transactions functionality 
        # redis token is valid for 1 hour
        session_key = await auth_backend.generate_session_token(str(user.id))
        print("\n-----\nSERVER LOG:", f"user {user.id} logged in\n-----\n")
        
    async def on_after_register(self, user_data: UserCreate, request: Optional[Request] = None):
        # /register handler - creates token and sends email for new user verification
        # verification token and construct the verification URL
        verify_token = await generate_verification_token(user_data)
        verification_url = f"http://localhost:8000/auth/verify?verify_token={verify_token}"
        email = EmailSchema(email_addresses = [user_data.email])
        print("\n-----\nSERVER LOG:",  f"User {user_data.fullname} registered and needs verification: {verify_token}.\n-----\n")
        await email_utils.send_verification_email(email, verification_url)
        
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        #TODO: call save_user
        save_user(user)
        # /verify handler: user is rerouted to frontend, this is just for logging   
        print("\n-----\nSERVER LOG:", f"user {user.id} verified\n-----\n")
    
    async def validate_new_user_password(self, password: str, user: UserCreate) -> None:
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
        await redis.set(f"{reset_token}", str(user.id))
        reset_url = f"http://localhost:8000/auth/reset-password?reset_token={reset_token}"
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_reset_email(email, reset_url)
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. \nReset token: {reset_token}\n-----\n")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_change_confirmation(email)
        print("\n-----\nSERVER LOG: ", f"user {user.id} successfully reset their password\n-----\n")
        
    async def on_after_update(self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"User {user.id} updated: {update_dict}\n-----\n")
    
    # TODO: send email confirmation to user with link confirming account deletion
    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} is going to be deleted\n-----\n")
         
    # TODO: on_before_delete html button leads here - user confirmed deletion     
    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} successfully deleted\n-----\n")
    
# UserManager is injected at runtime: get_user_db injects the fastapi-users database instance 
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)