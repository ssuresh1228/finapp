from fastapi import APIRouter
from server.model.user_model import User
from server.util.user_manager import get_user_manager
from server.util.auth_utils import auth_backend
from server.schemas.user_schema import UserRead, UserUpdate
from fastapi_users import FastAPIUsers
from beanie import PydanticObjectId
from fastapi.responses import JSONResponse

router = APIRouter()

fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager, 
    [auth_backend]
)

@router.get("/welcome")
async def after_verification():
    return JSONResponse ({ "message": "success!"})