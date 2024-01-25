from server.model.user_model import User
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi_users_db_beanie import ObjectIDIDMixin 
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from server.schemas.user_schema import *
from fastapi.templating import Jinja2Templates # temp for functionality until frontend
from bson import ObjectId
from loguru import logger

class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):   
    
    @logger.catch
    async def get_user_by_id(self, user_id: str):
        # get user ID and check if valid
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            raise ValueError("Error - invalid user ID format")
        user = await User.find_one(User.id == user_oid)
        if not user:
            raise ValueError("Error - user not found")
        return user
    
    @logger.catch
    async def check_user_exists(self, request: UserReadValidator):
        # query for user with same email - raise an error if they exist 
        email_to_check = request.email
        existing_user = await User.find_one(User.email == request.email)
        if existing_user:
            raise ValueError("Error: user already registered, log in instead")
        return None
    
    @logger.catch
    async def validate_new_user_password(self, request: UserRegistrationValidator) -> None:
        entered_password = request.hashed_password
        if len(entered_password) < 5:
            raise InvalidPasswordException(reason = "Password must be at least 5 characters")
        if request.email in entered_password:
            raise InvalidPasswordException(reason = "Password cannot contain an email address")
        if request.phone_number in entered_password:
            raise InvalidPasswordException(reason = "Password cannot contain a phone number")
        if request.fullname in entered_password:
            raise InvalidPasswordException(reason = "Password cannot contain a name")
    
    @logger.catch
    async def validate_reset_password(self, new_password: str):
        if len(new_password) < 5:
            raise InvalidPasswordException("Password must be longer than 5 characters.")
    
    @logger.catch
    async def get_user_by_email(self, email:str):
        user = await User.find_one(User.email == email)
        if not user:
            raise ValueError("Error - user email does not exist or account is not verified")
        return user
    
    #@logger.catch
    async def user_registration(self, registration_request: UserRegistrationValidator, email_manager, auth_manager):
        try:
            # check if user already exists
            user = await self.check_user_exists(registration_request)
            if(user):
                raise ValueError("User already registered")
            else:
            # otherwise validate their password and hash it on sucess
                await self.validate_new_user_password(registration_request)
                saved_password = await auth_manager.hash_password(registration_request.hashed_password) 
                registration_request.hashed_password = saved_password
                verify_token = await auth_manager.generate_verification_token(registration_request)
                await email_manager.send_verification_email(registration_request.email, verify_token)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    #@logger.catch
    async def verify_user(self, request: VerificationRequest, auth_manager):
        try: 
            # check if token is valid 
            if(request.verify_token):
                user_redis_json = await auth_manager.deserialize_redis(request.verify_token)
                # deserialize if valid 
                user_data = UserCreateValidator.model_validate_json(user_redis_json)
            else:
                raise ValueError("token does not exist or timed out - register again")
        
            # check if user already exists in db
            existing_user = await self.check_user_exists(user_data)
            
            # raise error if user exists
            if(existing_user):
                raise ValueError("Error - user already has an account")
            else:
                # create a new user otherwise
                #print("\n\nUSER_DATA.DICT(): ", user_data.dict(), "\n\n")
                new_user = User(**user_data.dict(), is_verified=True)
                    
            # save user and delete cached data + token
            await new_user.save()
            await auth_manager.del_redis_token(request.verify_token)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"message": f"{new_user.email} verification was successful"}
    
    @logger.catch
    async def forgot_password(self, password_request: ForgotPasswordRequest, email_manager, auth_manager):
        # attempt to get the user's email address 
        try:
            user = await self.get_user_by_email(password_request.email)
            if user is None:
                raise HTTPException(status_code=404, detail = "Error - user does not exist")
            # on success, generate reset token and send it via email 
            user_id_string = str(user.id)
            reset_token = await auth_manager.generate_password_reset_token(user_id_string)
            await email_manager.send_password_reset_email(user.email, reset_token)
            return {"message": f"user {user.email} was sent an email to reset their password"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @logger.catch
    async def user_login(self, request: UserLoginValidator, response: Response, auth_manager):
        # attempt to find user by email 
        try: 
            saved_user = await self.get_user_by_email(request.email)
            
            if saved_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # validate entered password
            valid_password = await auth_manager.verify_password(request.password, saved_user.hashed_password)
            if not valid_password:
                raise HTTPException(status_code=401, detail="Incorrect password")
            
            # generates a session token and sets cookie in response on successful login 
            session_key = await auth_manager.generate_session_token(str(saved_user.id), response)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))       

    #@logger.catch
    async def update_user_password(self, reset_request: PasswordResetRequest, email_manager, auth_manager):
        try: 
            user_id = await auth_manager.get_redis_token(reset_request.reset_token)
            if not user_id:
                raise HTTPException(status_code=400, detail = "Error - invalid or expired token")
            user = await self.get_user_by_id(user_id)
            await self.validate_reset_password(reset_request.new_password)    
            new_password = await auth_manager.hash_password(reset_request.new_password)
            user.hashed_password = new_password
            await user.save()
            await auth_manager.del_redis_token(reset_request.reset_token)
            # send email confirming password reset 
            await email_manager.send_password_change_confirmation(user.email)
        except ValueError as e:
            raise HTTPException(status_code=400, detail = str(e))
    
    @logger.catch
    async def user_logout(self, request: Request, auth_manager):
        session_key = request.cookies.get("session_key")
        if not session_key:
            return JSONResponse(status_code=401, content={"detail": "No active session found"})

        user_id = await auth_manager.get_redis_token(session_key)
        if not user_id:
            return JSONResponse(status_code=401, content={"detail": "Invalid user or session key"})

        deleted_count = await auth_manager.del_redis_token(session_key)
        if deleted_count == 0:
            return JSONResponse(status_code=500, content={"detail": "Failed to delete session key"})

        response = Response()
        response.delete_cookie(key="session_key")
        await del_redis_token(session_key)
        return JSONResponse(content={"detail": "Logout successful, session ended"})