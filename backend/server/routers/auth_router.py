from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_users import FastAPIUsers, InvalidPasswordException
from server.model.user_model import User 
from server.schemas.user_schema import *
from server.schemas.email_schema import *
from server.util.auth_utils import auth_backend, redis
from server.util.user_manager import get_user_manager
from passlib.hash import bcrypt
from pydantic import ValidationError
from fastapi.templating import Jinja2Templates # temp for testing 

# user model used for CRUD ops (on successful validation)
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend] # single auth backend still needs to be passed as a single element list
)

custom_auth_router = APIRouter()

# creates "/login" and "/logout" routes for auth backend (Redis)
# calls on_after_login() in UserManager after successful login 
#auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True) 

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
    hashed_password = bcrypt.hash(request.password)
    # create UserCreate instance with the hashed password 
    user_data = UserCreate(
        email = request.email, 
        fullname = request.fullname,
        username = request.username,
        phone_number = request.phone_number,
        password = hashed_password
    )
    # call handler method 
    await user_manager.on_after_register(user_data)

@custom_auth_router.get("/login")
async def login(request: UserLoginRequest, user_manager = Depends(get_user_manager)):
    # grab the username and password 
    email = request.user_email
    password = request.user_password   
    # pass these to login handler for querying user and verifying password 
    user = await user_manager.user_login(email, password)
    # raise error if user isn't found
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials entered.")
    else:
        # call on_after_login on success
        # TODO: set cookie on successful response
        response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True)
        user = await user_manager.on_after_login(user)
    
#TODO: logout + redis session invalidation 
# async def logout(request: UserLogoutRequest, user_manager = Depends(get_user_manager)):

@custom_auth_router.get("/verify")    
async def user_verification(verify_token: str, user_manager = Depends(get_user_manager)):
    # get the user's cached json data from redis
    user_redis_json = await redis.get(f"{verify_token}")
    
    #if user data exists, deserialize and validate it against UserCreate
    if user_redis_json:
        user_data = UserCreate.model_validate_json(user_redis_json)
        # if successful and doesn't exist already, save the user 
        new_user = await user_manager.save_new_user(user_data)
        # call after successful verification
        user_manager.on_after_verify(new_user)
        # Invalidate the verification token 
        await redis.delete(user_redis_json)
        # redirects to placeholder page (replace with frontend main page)
        return RedirectResponse(url="http://localhost:8000/docs", status_code=303)
    else:
        raise HTTPException(status_code=400, detail= "User not found or token is invalid")
    
#/forgot-password: calls on_after_forgot_password handler if user exists to generate a token for password reset
@custom_auth_router.get("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, user_manager = Depends(get_user_manager)):
    # get the user's email from the request
    user = await user_manager.get_user_by_email(request.password_email)
    # if the user exists, generate a password reset token + URL, then mail it to them
    if user:
        # send the reset password email
        await user_manager.on_after_forgot_password(user)  
        return {"message": "If user with that email exists, a password reset email was sent"}
        

templates = Jinja2Templates(directory="backend/server/util/templates")
@custom_auth_router.get("/reset-password")
async def get_password_reset_form(request: Request, reset_token:str):
    # get the token from /forgot-password 
    user_id = await redis.get(f"{reset_token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid/Expired Token")
    # render password reset form 
    return templates.TemplateResponse("password_reset_form.html", {"request": request, "reset_token": reset_token})

#TODO: POST /reset-password
#@custom_auth_router.post("/reset-password")
#async def reset_password(request: PasswordResetForm, user_manager = Depends(get_user_manager)):
