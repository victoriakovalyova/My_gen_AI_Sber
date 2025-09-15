from fastapi import APIRouter, Depends
from app.schemas.user import UserRead
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user