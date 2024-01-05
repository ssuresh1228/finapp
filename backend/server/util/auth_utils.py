import redis.asyncio as redis
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, RedisStrategy
from server.model.user_model import User
from server.database import get_user_db
from fastapi_users import FastAPIUsers
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate, UserRegistrationRequest
import secrets

# --- strategy --- 
# a token is generated and associated with a user_id in DB
# on each request, retrieve this token from redis to get corresponding user_id
# on logout, redis deletes user's session key, invalidating their session

# create redis connection
# docker: docker run -p 6379:6379 --name redis -d redis
redis = redis.from_url("redis://localhost:6379", decode_responses=True)

def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)

# cookie transport config
cookie_transport = CookieTransport(
    cookie_secure = True, # cookies sent over HTTPS
    cookie_httponly = True # prevent client-side cookie access
)

# redis auth backend config
#redis_strategy = get_redis_strategy()
auth_backend = AuthenticationBackend(
    name = "redis_cookie",
    transport = cookie_transport,
    get_strategy = get_redis_strategy,
)

# generates tokens for user verification 
# temporarily cache user data in redis 
async def generate_verification_token(user_data: UserRegistrationRequest) -> str:
    verify_token = "verify_" + secrets.token_urlsafe(32)
    # store token with reference to user email with 10 min expiration
    await redis.set(f"{verify_token}", user_data.model_dump_json(), ex=600)
    return verify_token

# generates user session keys
async def generate_session_token(user_id: str) -> str:
    session_key = "session_" + secrets.token_urlsafe(32)
    # store key with reference to user ID + 1 day expiration time
    await redis.set(f"{session_key}", user_id, ex=86400)
    return session_key

# generates password reset tokens
async def generate_password_reset_token(user_id: str) -> str: 
    # generate password token with 10 min expiration
    password_token = "reset_password_" + secrets.token_urlsafe(32)
    await redis.set(f"{password_token}", user_id, ex=600)
    return password_token