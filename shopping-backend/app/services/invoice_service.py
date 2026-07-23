from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database.order_model import Order

from app.utils.pdf_generator import generate_invoice


def download_invoice(
    db: Session,
    current_user,
    order_id: int,
):

    order = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.user),
        )
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

    return generate_invoice(order)