from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import admin_required

from app.database.user_model import User

from app.schemas.category import CategoryCreate

from app.services.category_service import (
    create_category,
    get_all_categories,
    update_category,
    delete_category,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("/")
def list_categories(
    db: Session = Depends(get_db),
):

    return get_all_categories(db)


@router.post("/")
def create_category_endpoint(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    return create_category(
        db,
        payload.name,
        payload.description,
    )


@router.put("/{category_id}")
def update_category_endpoint(
    category_id: int,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    category = update_category(
        db,
        category_id,
        payload.name,
        payload.description,
    )

    if category is None:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


@router.delete("/{category_id}")
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    deleted = delete_category(
        db,
        category_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return {
        "message": "Category deleted successfully"
    }