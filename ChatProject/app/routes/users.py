from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut, summary="Поточний користувач (потрібен Bearer токен)")
def read_me(current: User = Depends(get_current_user)):
    return current
