from fastapi import APIRouter
from server.model.user_model import User, UserCreate
router = APIRouter()

# user validation
@router.post("/register")
async def create_user(user_data: UserCreate):
    user = User(email=user_data.email, 
                fullname=user_data.fullname, 
                username=user_data.username, 
                phone_number=user_data.phone_number, 
                hashed_password=user_data.hashed_password)
    await user.insert()
    return {"message": "User created successfully", "user": user}