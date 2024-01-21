import redis.asyncio as redis
from server.schemas.user_schema import UserRegistrationValidator
import secrets
import bcrypt
from server.schemas.user_schema import VerificationRequest
from fastapi import Response

# --- strategy --- 
# a token is generated and associated with a user_id in DB
# on each request, retrieve this token from redis to get corresponding user_id
# on logout, redis deletes user's session key, invalidating their session
redis = redis.from_url("redis://localhost:6379", decode_responses=True)

class AuthManager:
    # create redis isntance: docker run -p 6379:6379 --name redis -d redis
    
    # generates tokens for user verification 
    # temporarily cache user data + token in redis then deletes on expiration/verification
    async def generate_verification_token(self, user_data: UserRegistrationValidator) -> str:
        verify_token = "verify_" + secrets.token_urlsafe(32)
        # store token with reference to user with 5 min expiration
        await redis.set(f"{verify_token}", user_data.model_dump_json(), ex=300)
        return verify_token

    # generates user session keys
    async def generate_session_token(self, user_id: str, response: Response):
        session_key = "session_" + secrets.token_urlsafe(32)
        # store key with reference to user ID + 1 day expiration time
        await redis.set(f"{session_key}", user_id, ex=86400)
        response.set_cookie(
            key="session_key",
            value=session_key,
            httponly=True, # prevents client side access
            secure=True, #  cookie only sent over HTTPS if true (false for local testing)
            max_age=86400
        )
        return session_key

    # generates password reset tokens
    async def generate_password_reset_token(self, user_id: str) -> str: 
        # generate password token with 10 min expiration
        password_token = "reset_password_" + secrets.token_urlsafe(32)
        await redis.set(f"{password_token}", user_id, ex=600)
        return password_token

    # hash password for storing
    async def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')

    # verify entered password against its hashed equivalent for logging in 
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    # gets verification token to extract user data from 
    async def get_redis_token(self, token: str):
        return await redis.get(f"{token}")
        
    async def del_redis_token(self, token: str):
        if token: 
            await redis.delete(f"{token}")
        else: 
            raise ValueError("token does not exist")
    
    async def deserialize_redis(self, token:str):
        #verify_token = request.json() ["verify-token"]
        #verify_token = request.verify_token
        user_redis_json = await redis.get(token)
        if not user_redis_json:
            raise ValueError("User not found or token has expired")
        return user_redis_json
