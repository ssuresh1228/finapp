from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_users import FastAPIUsers
from server.model.user_model import User 
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate
from server.schemas.email_schema import EmailSchema, ForgotPasswordRequest, ResetPasswordRequest
from server.util.auth_backend import auth_backend, redis
from server.util.user_manager import get_user_manager
from server.util.email_utils import get_user_by_email
import server.util.auth_backend

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


#redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
# /verify: gets a user's redis verification and verifies if they exist and if token is valid
custom_auth_router = APIRouter()

@custom_auth_router.get("/verify")    
async def user_verification(verify_token: str, user_manager = Depends(get_user_manager)):
    # get the user's ID from the redis token 
    user_id = await redis.get(f"{verify_token}")
    # if the user id exists, check if they exist in DB
    if user_id:
        user = await user_manager.get(user_id)
        # if the user exists, verify + save them then reroute to front end welcome page
        if user:
            user.is_verified = True
            await user.save()
            # redirects to placeholder page (replace with frontend main page)
            return RedirectResponse(url="http://localhost:8000/docs", status_code=303)
            # Invalidate the token by deleting it from Redis
            await redis.delete(f"password_reset:{token}")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
#/forgot-password: calls on_after_forgot_password handler if user exists to generate a token for password reset
@custom_auth_router.get("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, user_manager = Depends(get_user_manager)):
    # get the user's email from the request
    user = await get_user_by_email(request.password_email)
    # if the user exists, generate a password reset token + URL, then mail it to them
    if user:
        # send the reset password email
        await user_manager.on_after_forgot_password(user)  
        return {"message": "If user with that email exists, a password reset email was sent"}
        
# TODO: /reset-password: resets user password using token generated from /forgot-password
@custom_auth_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, user_manager = Depends(get_user_manager)):
    # get the token from /forgot-password 
    user_id = await redis.get(f"password_reset:{request.reset_token}")
    # raise an error when an expired/invalid token is used 
    if not user_id:
        raise HTTPException(status_code = 400, detail = "invalid/expired token")
    
    # get the user id from the token - raise error if not a match 
    user = await user_manager.get(user_id)
    if not user: 
        raise HTTPException(status_code = 404, detail = "user not found")
    
    # validate then update user's new password and delete redis password_reset token
    await user_manager.validate_reset_password(request.new_password)
    await redis.delete(f"deleting {user_id} password_reset:{request.reset_token}")
    # call handler to send password change confirmation email:
    await user_manager.on_after_reset_password(user)
    #redirect to login page - docs page as placeholder
    