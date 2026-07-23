from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import user_required

from app.database.user_model import User

from app.schemas.payment import PaymentRequest

from app.services.payment_service import (
    process_payment,
    get_payment,
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/{order_id}")
def pay_order(
    order_id: int,
    payload: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return process_payment(
        db,
        current_user,
        order_id,
        payload.payment_method,
    )


@router.get("/{order_id}")
def payment_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return get_payment(
        db,
        current_user,
        order_id,
    )