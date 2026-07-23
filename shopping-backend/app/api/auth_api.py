from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import UserCreate
from app.schemas.user import UserLogin

from app.services.auth_service import (
    register_user,
    login_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    new_user = register_user(
        db,
        user.email,
        user.password,
    )

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    return {
        "message": "User Registered Successfully"
    }


@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):

    token = login_user(
        db,
        user.email,
        user.password,
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }