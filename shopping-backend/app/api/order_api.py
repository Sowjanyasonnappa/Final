from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import (
    user_required,
    admin_required,
)

from app.database.user_model import User

from app.schemas.order import CheckoutRequest

from app.services.order_service import (
    checkout,
    get_user_orders,
    get_order,
    cancel_order,
    update_order_status,
    get_order_tracking,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/checkout")
def checkout_order(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return checkout(
        db,
        current_user,
        payload.shipping_address,
        payload.coupon_code,
    )


@router.get("/")
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return get_user_orders(
        db,
        current_user,
    )


@router.get("/{order_id}")
def get_single_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    order = get_order(
        db,
        current_user,
        order_id,
    )

    if order is None:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order


@router.post("/{order_id}/cancel")
def cancel_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    cancelled = cancel_order(
        db,
        current_user,
        order_id,
    )

    if cancelled is None:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return cancelled

@router.put("/{order_id}/status")
def change_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    return update_order_status(
        db,
        order_id,
        status,
    )
@router.get("/{order_id}/tracking")
def order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return get_order_tracking(
        db,
        order_id,
    )