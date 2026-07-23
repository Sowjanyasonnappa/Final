from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user_admin import (
    UserRoleUpdate,
)

from app.services.user_service import (
    get_all_users,
    get_user,
    update_role,
    delete_user,
)

from app.auth.oauth2 import admin_required

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return get_all_users(db)


@router.get("/{user_id}")
def fetch_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    user = get_user(
        db,
        user_id,
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.put("/{user_id}/role")
def change_role(
    user_id: int,
    role: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    updated = update_role(
        db,
        user_id,
        role.role,
    )

    if updated is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "Role Updated Successfully",
        "user": updated,
    }


@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    deleted = delete_user(
        db,
        user_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "User Deleted Successfully"
    }