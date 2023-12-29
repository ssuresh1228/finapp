from server.model.user_model import User, UserCreate
from server.database import get_user_db
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi_users_db_beanie import ObjectIDIDMixin 
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi import Depends, Request
from typing import Optional, Union, Dict, Any
from beanie import PydanticObjectId
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

SECRET = "SECRET"
    
# UserManager class: core logic of user management
# ID Parser Mixin: ObjectIDIDMixin + PydanticObjectId used for MongoDB's ObjectID
class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    #TODO: methods need to be overloaded - print statments used as placeholders
    #TODO: define & use Jinja2 HTML templates in each method - send over email

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
            logic after a user registers successfully

            Args:
                self: instance of the class on which the method is being called, used to access other attributes/methods of UserManager class when needed
                user (User): current user
                request (Optional[Request], optional): optional FastAPI request object that triggered the operation. Defaults to None.
        """
        print("User {user.id} registered")
    
    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """
            provides a token for the user to reset their password

            Args:
                self - instance of the class on which the method is being called, used to access other attributes/methods of UserManager class when needed
                user (User): current user
                token (str): _description_
                request (Optional[Request], optional): _description_. Defaults to None.
        """
        print("user {user.id} forgot their password. Reset token: {token}")

    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Request] = None):
        """
            what to do after a user logs in 

            Args:
                user (User): current user
                request (Optional[Request], optional): Optional FastAPI request obj that triggered the operation. Defaults to None.
                response (Optional[Request], optional): Optional response built by transport. Defaults to None.
        """
        print("user {user.id} logged in")
        
    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        """ 
            what to do after a successful verification request
            (send an email with a link and token to the user so they can verify their email address)
            
            Args:
                user (User): current user
                token (str): verification token
                request (Optional[Request], optional): optional FastAPI request object that triggered the operation. Defaults to None.
        """
        print("user {user.id} requested verification. Verification token: {token}")
    
    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        """
            what to do after successful user verification
            useful for sending future emails (e.g. for resetting passwords)

            Args:
                user (User): current user
                request (Optional[Request], optional): optional FastAPI obj that triggered this operation. Defaults to None.
        """
        print("user {user.id} verified")
    
    async def validate_password(self, password: str, user: Union[UserCreate, User]) -> None:
        """
            returns None when password is valid, raises an InvalidPasswordException otherwise

            Args:
                password (str): password to validate
                user (Union[UserCreate, User]): user model being validated

            Raises:
            InvalidPasswordException: password is too short
            InvalidPasswordException: has email address
            InvalidPasswordException: contains phone number
            InvalidPasswordException: contains a
        """
        if len(password < 5):
            raise InvalidPasswordException(reason = "Password must be at least 5 characters")
        if user.email in password:
            raise InvalidPasswordException(reason = "Password cannot contain an email address")
        if user.phone_number in password:
            raise InvalidPasswordException(reason = "Password cannot contain a phone number")
        if user.fullname in password:
            raise InvalidPasswordException(reason = "Password cannot contain a name")
    
    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """
            what to do after a successful forgot password request - send an email with link and token for resetting password

            Args:
                user (User): current user
                token (str): token used for resetting password
                request (Optional[Request], optional): optional FastAPI request obj that triggered this operation. Defaults to None.
        """
        print("user {user.id} forgot password. Reset token: {token}")
        
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        """
            what to do after a user resets their password

            Args:
                user (User): _description_
                request (Optional[Request], optional): _description_. Defaults to None.
        """
        print("user {user.id} successfully reset their password")
    
    async def on_after_update(self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None):
        """
            handles what to do after user updates

            Args:
                user (User): current user
                update_dict (Dict[str, Any]): dictionary with updated user fields
                request (Optional[Request], optional): optional FastAPI request obj that triggered the operation. Defaults to None.
        """
        print("User {user.id} updated: {update_dict}")
    
    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        """
            what to do before a user deletes their account

            Args:
                user (User): current user
                request (Optional[Request], optional): optional FastAPI obj that triggered this response. Defaults to None.
        """
        print("user {user.id} is going to be deleted")
        
    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        """
            what to do after a user deletes their account

            Args:
                user (User): current user
                request (Optional[Request], optional): optional FastAPI obj that triggered this response. Defaults to None.
        """
        print("user {user.id} successfully deleted")
    
# UserManager is injected at runtime: get_user_db is used here to inject the database instance 
async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    """
        UserManager is injected at runtime

        Args:
            user_db (BeanieUserDatabase, optional): injects database instance. Defaults to Depends(get_user_db).

        Yields:
            UserManager(fastAPI-users database)
    """
    yield UserManager(user_db)