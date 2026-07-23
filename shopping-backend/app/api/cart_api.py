from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import user_required

from app.database.user_model import User

from app.schemas.cart import CartItemCreate
from app.schemas.cart import CartItemUpdate

from app.services.cart_service import (
    add_to_cart,
    clear_cart,
    get_cart,
    remove_cart_item,
    update_cart_item,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get("/")
def view_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    return get_cart(
        db,
        current_user,
    )


@router.post("/items")
def add_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):
    return add_to_cart(
        db,
        current_user,
        payload.product_id,
        payload.quantity,
    )


@router.put("/items/{item_id}")
def update_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    updated = update_cart_item(
        db,
        current_user,
        item_id,
        payload.quantity,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    return updated


@router.delete("/items/{item_id}")
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    deleted = remove_cart_item(
        db,
        current_user,
        item_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    return {
        "message": "Item removed from cart"
    }


@router.delete("/")
def clear_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    clear_cart(
        db,
        current_user,
    )

    return {
        "message": "Cart cleared"
    }