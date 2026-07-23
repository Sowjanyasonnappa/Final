import uuid
import asyncio

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.order_model import Order
from app.database.payment_model import Payment
from app.database.user_model import User

from app.services.email_service import send_email

from app.utils.email_templates import payment_success


VALID_PAYMENT_METHODS = [
    "COD",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet",
]


def process_payment(
    db: Session,
    current_user: User,
    order_id: int,
    payment_method: str,
):

    if payment_method not in VALID_PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method",
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if payment.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Payment already completed",
        )

    payment.payment_method = payment_method

    payment.transaction_id = (
        str(uuid.uuid4())
        .replace("-", "")
        .upper()
    )

    payment.status = "Completed"

    order.payment_status = "Completed"

    db.commit()

    db.refresh(payment)

    asyncio.create_task(
        send_email(
            current_user.email,
            "Payment Successful",
            payment_success(
                current_user,
                payment,
            ),
        )
    )

    return {
        "payment_id": payment.id,
        "transaction_id": payment.transaction_id,
        "payment_method": payment.payment_method,
        "amount": payment.amount,
        "status": payment.status,
    }


def get_payment(
    db: Session,
    current_user: User,
    order_id: int,
):

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment