from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import user_required

from app.database.user_model import User

from app.services.wishlist_service import (
    get_wishlist,
    add_to_wishlist,
    remove_from_wishlist,
)

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"],
)


@router.get("/")
def list_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return get_wishlist(
        db,
        current_user,
    )


@router.post("/{product_id}")
def add_wishlist_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    item = add_to_wishlist(
        db,
        current_user,
        product_id,
    )

    if item is None:

        raise HTTPException(
            status_code=400,
            detail="Product already exists in wishlist",
        )

    return item


@router.delete("/{product_id}")
def remove_wishlist_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    deleted = remove_from_wishlist(
        db,
        current_user,
        product_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Wishlist item not found",
        )

    return {
        "message": "Wishlist item removed successfully"
    }