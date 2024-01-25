from fastapi import APIRouter, Depends, Request, Response
from server.schemas.user_schema import *
from server.schemas.user_schema import *
from server.dependencies import get_user_manager, get_email_manager, get_auth_manager
from loguru import logger


custom_auth_router = APIRouter()

@custom_auth_router.post("/register")
async def user_registration(request: UserCreateValidator, user_manager = Depends(get_user_manager), email_manager = Depends(get_email_manager), auth_manager = Depends(get_auth_manager)):
    # check if user exists, validate their password meets requirements and hash on success
    await user_manager.user_registration(request, email_manager, auth_manager)

@custom_auth_router.post("/login")
async def login(login_request: UserLoginValidator, response: Response, user_manager = Depends(get_user_manager), auth_manager = Depends(get_auth_manager)):
    await user_manager.user_login(login_request, response, auth_manager)


@custom_auth_router.post("/logout")
async def logout(request: Request, user_manager = Depends(get_user_manager), auth_manager = Depends(get_auth_manager)):
    #return {"cookies": request.cookies}
    await user_manager.user_logout(request, auth_manager)

@custom_auth_router.post("/verify")    
async def user_verification(request: VerificationRequest, user_manager = Depends(get_user_manager), auth_manager = Depends(get_auth_manager)):
    await user_manager.verify_user(request, auth_manager)
       
@custom_auth_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, user_manager = Depends(get_user_manager), email_manager = Depends(get_email_manager), auth_manager = Depends(get_auth_manager)):
    # sends user an email with password reset link with token 
    await user_manager.forgot_password(request, email_manager, auth_manager)

@custom_auth_router.post("/reset-password")
async def reset_password(request: PasswordResetRequest, user_manager = Depends(get_user_manager), email_manager = Depends(get_email_manager), auth_manager = Depends(get_auth_manager)):
    # verifies reset password token sent from frontend 
    await user_manager.update_user_password(request, email_manager, auth_manager)