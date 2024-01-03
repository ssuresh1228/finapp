from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi_users import FastAPIUsers
from server.model.user_model import User 
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate
from server.schemas.email_schema import EmailSchema
from server.util.auth_backend import auth_backend 
from server.util.user_manager import get_user_manager
# from server.database import get_user_db
import redis.asyncio as redis

# configures routes for registration, authentication, login, password recovery, etc
# requires user model to be read, not its schema 

# user model used for CRUD ops (on successful validation)
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend] # single auth backend still needs to be passed as a single element list
)

# creates "/login" and "/logout" routes for auth backend (Redis)
# calls on_after_login() in UserManager after successful login 
auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True) 

# creates "/register" route for users to create a new account 
# calls on_after_register() in UserManager on success
# validates user's entered info against UserCreate schema to make sure it's valid 
registration_router = fastapi_users.get_register_router(UserRead, UserCreate)


# /forgot-password: generates a temporary token and calls on_after_forgot_password handler if user exists
# /reset-password: uses token generated in forgot-password to reset password
# calls on_after_forgot_password in UserManager on success
reset_password_router = fastapi_users.get_reset_password_router()


redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
# /verify: gets a user's redis verification and verifies if they exist and if token is valid
custom_verification_router = APIRouter()
@custom_verification_router.get("/verify")    
async def user_verification(verify_token: str, user_manager = Depends(get_user_manager)):
    # get the user's ID from the redis token 
    user_id = await redis_client.get(f"{verify_token}")
    # if the user id exists, check if they exist in DB
    if user_id:
        user = await user_manager.get(user_id)
        # if the user exists, verify + save them then reroute to front end welcome page
        if user:
            user.is_verified = True
            await user.save()
            # redirects to placeholder page
            return RedirectResponse(url="http://localhost:8000/docs", status_code=303)
        else:
            return {"error": "User not found"}
    else:
        return {"error": "Invalid or expired token"}