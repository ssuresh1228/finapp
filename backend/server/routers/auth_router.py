from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi_users import FastAPIUsers, InvalidPasswordException
from server.model.user_model import User 
from server.schemas.user_schema import *
from server.schemas.email_schema import *
from server.util.auth_utils import *
from server.util.user_manager import get_user_manager
from passlib.hash import bcrypt
from pydantic import ValidationError
import bcrypt
import server.util.auth_utils
# user model used for CRUD ops (on successful validation)
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend] # single auth backend still needs to be passed as a single element list
)

custom_auth_router = APIRouter()

@custom_auth_router.post("/register")
async def user_registration(request: UserRegistrationRequest, user_manager = Depends(get_user_manager)):
    # check if user already exists
    try: 
        await user_manager.check_user_exists(request.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # check if password meets requirements
    try:
        await user_manager.validate_new_user_password(request.password, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail = str(e.reason))
    # hash password when it meets requirements:
    # create UserCreate instance with the hashed password 
    user_hashed_password = auth_utils.hash_password(request.password)
    user_data = UserCreate(
        email = request.email,
        fullname = request.fullname,
        username = request.username,
        phone_number = request.phone_number,
        hashed_password = user_hashed_password
    )
    # call handler method 
    await user_manager.on_after_register(user_data)

#TODO: fix password comparison bug
@custom_auth_router.post("/login")
async def login(request: UserLoginRequest, user_manager = Depends(get_user_manager)):
    try:
        # attempt to fetch the user by email
        saved_user = await user_manager.get_user_by_email(request.entered_email)
    except ValueError as e:
        # If the user is not found, return a 400 error
        raise HTTPException(status_code=400, detail=str(e))
    
    # Verify the password
    if not verify_password(request.entered_password, saved_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    await user_manager.on_after_login(saved_user)
        
#TODO: logout + redis session invalidation 
# async def logout(request: UserLogoutRequest, user_manager = Depends(get_user_manager)):

@custom_auth_router.get("/verify")    
async def user_verification(verify_token: str, user_manager = Depends(get_user_manager)):
    #call handler method for deserialization and validation  
    try:
        await user_manager.save_verified_user(f"{verify_token}")
        # temp redirect to docs page
        return RedirectResponse(url="http://localhost:8000/docs", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@custom_auth_router.get("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, user_manager = Depends(get_user_manager)):
    # get the user's email from the request - call handler method 
    user = await user_manager.get_user_by_email(request.password_email)
    # if the user exists, generate a password reset token + URL, then mail it to them
    if user:
        # send the reset password email
        await user_manager.on_after_forgot_password(user)  
        return {"message": "If user with that email exists, a password reset email was sent"}

@custom_auth_router.get("/reset-password")
async def reset_password(request: Request, reset_token: str, user_manager = Depends(get_user_manager)):
    try:
        # call handler method on success
        return await user_manager.get_password_reset_form(request, reset_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@custom_auth_router.post("/reset-password")
async def reset_password(reset_token:str = Form(...), new_password:str = Form(...), user_manager = Depends(get_user_manager)):
    # get user id from the token - check if valid
    user_id = await redis.get(reset_token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Error - invalid or expired token")
    
    # call handler method to get the user obj from db by their id
    user = await user_manager.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Error - user not found")
    
    # validate user's new password - hash and update on success
    await user_manager.validate_reset_password(new_password)
    await user_manager.update_user_password(user, reset_token, new_password)

    #on success: delete token, call handler, redirect to placeholder
    redis.delete(reset_token)
    await user_manager.on_after_reset_password(user)
    return RedirectResponse(url="http://localhost:8000/docs", status_code=303)