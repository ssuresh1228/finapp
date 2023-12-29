import redis.asyncio
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, RedisStrategy
from server.model.user_model import User
from server.database import get_user_db
from fastapi_users import FastAPIUsers
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate
from server.util.user_manager import get_user_manager

# combines transport and backend strategy: redis token management + cookie transport

# --- strategy --- 
# a token is generated and associated with a user_id in DB
# on each request, retrieve this token from redis to get corresponding user_id
# on logout, the token is deleted from redis key store

# create redis connection
redis = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)

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