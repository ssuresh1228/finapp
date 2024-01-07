from server.model.user_model import User, UserCreate
from server.database import get_user_db
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi_users_db_beanie import ObjectIDIDMixin 
from fastapi_users.db import BeanieUserDatabase
from fastapi import Depends, Request, Response
from typing import Optional, Dict, Any
from beanie import PydanticObjectId
from server.util import email_utils
from server.util.auth_utils import *
from server.schemas.email_schema import EmailSchema
from server.schemas.user_schema import *
import bcrypt
from fastapi.templating import Jinja2Templates # temp for functionality until frontend
from bson import ObjectId

# core logic of user management
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):   
    async def check_user_exists(self, email: str):
        existing_user = await User.find_one(User.email == email)
        if existing_user: 
            raise ValueError("Error: user already exists, log in instead")
        return None
    
    async def save_verified_user(self, verify_token: str):
        # get the user's cached json data from redis
        user_redis_json = await redis.get(f"{verify_token}")
        
        #if user data exists, deserialize and validate it against UserCreate
        if not user_redis_json:
            raise ValueError("User not found or token is invalid")
        
        user_data = UserCreate.model_validate_json(user_redis_json)
       
        # check if user already exists in db
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise ValueError("User already verified - log in instead")
        
        new_user = User(**user_data.dict(), is_verified=True)
                
        # save user and delete cached data
        await new_user.save()
        await redis.delete(user_redis_json)
     
    async def get_user_by_email(self, email:str):
        user = await User.find_one(User.email == email)
        if not user:
            raise ValueError("Error - user email does not exist or account is not verified")
        return user
    
    async def get_user_by_id(self, user_id: str, request: Optional[Request] = None):
        # get user ID and check if valid
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            raise ValueError("Error - invalid user ID format")
        user = await User.find_one(User.id == user_oid)
        if not user:
            raise ValueError("Error - user not found")
        return user

    async def on_after_login(self, user: User, response: Response):
        #TODO: reports/transactions functionality 
        # generate a session token
        session_key = await generate_session_token(str(user.id))        
        # set session key as a cookie in response
        response.set_cookie(
            key="session_key", 
            value=session_key, 
            httponly=True,     # prevent client sice cookie access
            secure=False,      # cookie only sent over HTTPS (set to false for local testing)
            max_age=86400
        )
        
        print("\n-----\nSERVER LOG:", f"user {user.id} logged in\ncreating session key: {session_key}\n-----\n")
            
    async def on_after_register(self, user_data: UserCreate, request: Optional[Request] = None):
        # /register handler - creates token and sends email for new user verification
        # verification token and construct the verification URL
        verify_token = await generate_verification_token(user_data)
        verification_url = f"http://localhost:8000/auth/verify?verify_token={verify_token}"
        email = EmailSchema(email_addresses = [user_data.email])
        print("\n-----\nSERVER LOG:",  f"User {user_data.fullname} registered and needs verification: {verify_token}.\n-----\n")
        await email_utils.send_verification_email(email, verification_url)
    
    async def validate_new_user_password(self, password: str, user: UserCreate) -> None:
        if len(password) < 5:
            raise InvalidPasswordException(reason = "Password must be at least 5 characters")
        if user.email in password:
            raise InvalidPasswordException(reason = "Password cannot contain an email address")
        if user.phone_number in password:
            raise InvalidPasswordException(reason = "Password cannot contain a phone number")
        if user.fullname in password:
            raise InvalidPasswordException(reason = "Password cannot contain a name")
        
    async def validate_reset_password(self, new_password: str, request: Optional[Request] = None) -> None:
        if len(new_password) < 5:
            raise InvalidPasswordException("Password must be longer than 5 characters.")
    
    async def on_after_forgot_password(self, user: User, request: Optional[Request] = None):
        reset_token = await generate_password_reset_token(str(user.id))
        await redis.set(f"{reset_token}", str(user.id))
        reset_url = f"http://localhost:8000/auth/reset-password?reset_token={reset_token}"
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_reset_email(email, reset_url)
        print("\n-----\nSERVER LOG:", f"user {user.id} forgot password. \nReset token: {reset_token}\n-----\n")
    
    #temporarily using Jinja2 form for password reset functionality  
    async def get_password_reset_form(self, request: Request, reset_token: str):
        templates = Jinja2Templates("backend/server/util/templates")
        user_id = await redis.get(f"{reset_token}")
        if not user_id:
            raise Exception("Error - invalid password reset token")
        return templates.TemplateResponse("password_reset_form.html", {"request": request, "reset_token": reset_token})    

    async def update_user_password(self, user: User, reset_token: str, new_password: str, request: Optional[Request] = None):
        # validate user's new password - hash it on success
        new_hashed_password = bcrypt.hash(new_password)
        user.hashed_password = new_hashed_password
    
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        email = EmailSchema(email_addresses = [user.email])
        await email_utils.send_password_change_confirmation(email)
        print("\n-----\nSERVER LOG: ", f"user {user.id} successfully reset their password\n-----\n")
    
    async def on_after_update(self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"User {user.id} updated: {update_dict}\n-----\n")    
          
    # TODO: tie to a endpoint for frontend to use
    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} is going to be deleted\n-----\n")
         
    # TODO: tie to a endpoint for frontend to use     
    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print("\n-----\nSERVER LOG:", f"user {user.id} successfully deleted\n-----\n")
    
# UserManager dependency injection
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)