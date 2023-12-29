from beanie import PydanticObjectId
from fastapi import FastAPI, APIRouter
from fastapi_users import FastAPIUsers
from server.model.user_model import User 
from server.schemas.user_schema import UserCreate, UserRead, UserUpdate
from server.util.auth_backend import auth_backend 
from server.util.user_manager import get_user_manager
from server.database import get_user_db


# handles "/login" and "/logout" routes
# requires user model to be read, not its schema 
router = APIRouter()

# configures routes for registration, authentication, login, password recovery, etc 
"""fastapi_users = FastAPIUsers[User, PydanticObjectId](
    user_db = get_user_db, 
    auth_backends = auth_backend,
    user_model = User,
    user_create_schema = UserCreate,
    user_read_schema = UserRead,
    user_update_schema = UserUpdate,
    get_user_manager = get_user_manager
)"""

fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [auth_backend] # 1 auth backend still needs to be passed as a single element list
)

router = fastapi_users.get_auth_router(auth_backend, requires_verification=True) 