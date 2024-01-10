from fastapi import APIRouter, Depends, Request, HTTPException, Form, Response
from fastapi.responses import RedirectResponse, JSONResponse
from server.schemas.user_schema import *
from server.schemas.email_schema import *
from server.util.auth_utils import *
from server.util.user_manager import get_user_manager

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
    user_hashed_password = hash_password(request.password)
    user_data = UserCreate(
        email = request.email,
        fullname = request.fullname,
        username = request.username,
        phone_number = request.phone_number,
        hashed_password = user_hashed_password
    )
    # call handler method 
    await user_manager.on_after_register(user_data)

@custom_auth_router.post("/login")
async def login(request: UserLoginRequest, response:Response, user_manager = Depends(get_user_manager)):
    try:
        # attempt to fetch the user by email
        saved_user = await user_manager.get_user_by_email(request.entered_email)
    except ValueError as e:
        # If the user is not found, return a 400 error
        raise HTTPException(status_code=400, detail=str(e))
    
    # Verify the entered password
    if not verify_password(request.entered_password, saved_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    await user_manager.on_after_login(saved_user, response)

@custom_auth_router.post("/logout")
async def logout(request: Request, user_manager = Depends(get_user_manager)):
    session_key = request.cookies.get("session_key")
    if not session_key:
        return JSONResponse(status_code=401, content={"detail": "No active session found"})

    user_id = await redis.get(session_key)
    if not user_id:
        return JSONResponse(status_code=401, content={"detail": "Invalid user or session key"})

    deleted_count = await redis.delete(session_key)
    if deleted_count == 0:
        return JSONResponse(status_code=500, content={"detail": "Failed to delete session key"})

    response = Response()
    response.delete_cookie(key="session_key")
    return JSONResponse(content={"detail": "Logout successful, session ended"})

@custom_auth_router.get("/verify")    
async def user_verification(verify_token: str, user_manager = Depends(get_user_manager)):
    #call handler method for deserialization and validation  
    try:
        await user_manager.save_verified_user(f"{verify_token}")
        # temp redirect to docs page
        return RedirectResponse(url="http://localhost:8000/docs", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await redis.delete(verify_token)
        
@custom_auth_router.get("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, user_manager = Depends(get_user_manager)):
    try:
        # get the user's email from the request - call handler method 
        user = await user_manager.get_user_by_email(request.password_email)
        await user_manager.on_after_forgot_password(user)  
        return {"message": "If user with that email exists, a password reset email was sent"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
    await redis.delete(reset_token)
    await user_manager.on_after_reset_password(user)
    return RedirectResponse(url="http://localhost:8000/docs", status_code=303)