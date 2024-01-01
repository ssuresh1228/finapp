from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter
from fastapi_users import FastAPIUsers
from server.model.user_model import User 
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate
from server.util.auth_backend import auth_backend 
from server.util.user_manager import get_user_manager
from server.database import get_user_db

# configures routes for registration, authentication, login, password recovery, etc
# requires user model to be read, not its schema 
auth_router = APIRouter()

# user model used for CRUD ops (on successful validation)
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend] # 1 auth backend still needs to be passed as a single element list
)

"""
use user schemas to validate data:
======
UserCreate: validates incoming data for a new user before creating a new user model in db
UserRead: user data displayed/used on frontend (i.e. doesn't include hashed password field)
"""

# creates "/login" and "/logout" routes for auth backend (Redis)
# calls on_after_login() in UserManager after successful login 
auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True) 

# creates "/register" route for users to create a new account 
# calls on_after_register() in UserManager on success
# validates user's entered info against UserCreate schema to make sure it's valid 
registration_router = fastapi_users.get_register_router(UserRead, UserCreate)

# creates "/request-verify-token" and "/verify" routes to manage user email verification 
# calls on_after_verify() in UserManager on success 
#TODO: fix /verify token not validating generated token 
verification_router = fastapi_users.get_verify_router(UserRead)

# creates "/forgot-password" and "/reset-password" routes to reset user password
# calls on_after_forgot_password in UserManager on success
reset_password_router = fastapi_users.get_reset_password_router()