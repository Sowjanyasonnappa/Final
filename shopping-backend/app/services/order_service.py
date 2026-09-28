from datetime import datetime, timezone
import asyncio

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.cart_model import CartItem
from app.database.models import Product
from app.database.order_model import Order
from app.database.order_item_model import OrderItem
from app.database.payment_model import Payment
from app.database.user_model import User
from app.database.coupon_model import Coupon
from app.database.order_tracking_model import OrderTracking

from app.services.email_service import send_email

from app.utils.email_templates import (
    order_confirmation,
    shipped,
    delivered,
    cancelled,
)


def _send_email_safely(recipient, subject, body):
    coroutine = send_email(recipient, subject, body)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coroutine)
    else:
        loop.create_task(coroutine)


def _coupon_is_expired(expiry_date):
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    return expiry_date < datetime.now(timezone.utc)


def checkout(
    db: Session,
    user: User,
    shipping_address: str,
    coupon_code: str | None = None,
):

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty",
        )

    total_amount = 0.0
    order_items = []

    for cart_item in cart_items:

        product = (
            db.query(Product)
            .with_for_update()
            .filter(Product.id == cart_item.product_id)
            .first()
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {cart_item.product_id} not found",
            )

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}",
            )

        total_amount += (
            product.price * cart_item.quantity
        )

        order_items.append(
            (
                product,
                cart_item.quantity,
            )
        )

    discount_amount = 0.0
    coupon = None

    if coupon_code:

        coupon = (
            db.query(Coupon)
            .filter(
                Coupon.code == coupon_code.upper(),
                Coupon.active == 1,
            )
            .first()
        )

        if (
            coupon is None
            or _coupon_is_expired(coupon.expiry_date)
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid coupon",
            )

        discount_amount = (
            total_amount
            * coupon.discount_percentage
            / 100
        )

    final_amount = round(
        total_amount - discount_amount,
        2,
    )

    try:

        order = Order(
            user_id=user.id,
            total_amount=final_amount,
            status="Pending",
            payment_status="Pending",
            shipping_address=shipping_address,
            coupon_code=(
                coupon.code if coupon else None
            ),
            discount_amount=discount_amount,
        )

        db.add(order)

        db.flush()

        tracking = OrderTracking(
            order_id=order.id,
            status="Pending",
            remarks="Order Created",
        )

        db.add(tracking)

        for product, quantity in order_items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price,
            )

            db.add(order_item)

            product.stock -= quantity

        payment = Payment(
            order_id=order.id,
            amount=final_amount,
            payment_method="COD",
            status="Pending",
        )

        db.add(payment)

        db.query(CartItem).filter(
            CartItem.user_id == user.id
        ).delete()

        db.commit()

        db.refresh(order)

        _send_email_safely(
            user.email,
            "Order Confirmation",
            order_confirmation(user, order),
        )

        return order

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    from sqlalchemy.orm import joinedload


def get_user_orders(
    db: Session,
    user: User,
):

    return (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.id.desc())
        .all()
    )


def get_order(
    db: Session,
    user: User,
    order_id: int,
):

    return (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.payments),
            joinedload(Order.user),
        )
        .filter(
            Order.user_id == user.id,
            Order.id == order_id,
        )
        .first()
    )


def cancel_order(
    db: Session,
    user: User,
    order_id: int,
):

    order = (
        db.query(Order)
        .options(joinedload(Order.user))
        .with_for_update()
        .filter(
            Order.user_id == user.id,
            Order.id == order_id,
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Order already cancelled",
        )

    if order.status not in {"Pending", "Confirmed"}:
        raise HTTPException(
            status_code=400,
            detail="Only pending or confirmed orders can be cancelled",
        )

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product is not None:
            product.stock += item.quantity

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if payment is not None and payment.status == "Completed":
        payment.status = "Refunded"
        order.payment_status = "Refunded"
    else:
        order.payment_status = "Pending"

    order.status = "Cancelled"

    tracking = OrderTracking(
        order_id=order.id,
        status="Cancelled",
        remarks="Order Cancelled",
    )

    db.add(tracking)

    db.commit()

    db.refresh(order)

    _send_email_safely(
        user.email,
        "Order Cancelled",
        cancelled(user, order),
    )

    return order


def update_order_status(
    db: Session,
    order_id: int,
    status: str,
):

    valid_status = [
        "Pending",
        "Confirmed",
        "Packed",
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Cancelled",
        "Returned",
        "Refunded",
    ]

    if status not in valid_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status",
        )

    order = (
        db.query(Order)
        .options(joinedload(Order.user))
    .with_for_update()
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    allowed_transitions = {
        "Pending": {"Confirmed", "Cancelled"},
        "Confirmed": {"Packed", "Cancelled"},
        "Packed": {"Shipped"},
        "Shipped": {"Out for Delivery", "Delivered"},
        "Out for Delivery": {"Delivered"},
        "Delivered": {"Returned"},
        "Returned": {"Refunded"},
        "Cancelled": set(),
        "Refunded": set(),
    }
    if status != order.status and status not in allowed_transitions.get(order.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move order from {order.status} to {status}",
        )

    if status == order.status:
        raise HTTPException(
            status_code=400,
            detail=f"Order is already {status}",
        )

    if status == "Cancelled":
        if order.status == "Cancelled":
            raise HTTPException(status_code=400, detail="Order already cancelled")
        if order.status not in {"Pending", "Confirmed"}:
            raise HTTPException(
                status_code=400,
                detail="Only pending or confirmed orders can be cancelled",
            )
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if payment is not None and payment.status == "Completed":
            payment.status = "Refunded"
            order.payment_status = "Refunded"
        else:
            order.payment_status = "Pending"
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product is not None:
                product.stock += item.quantity

    order.status = status

    tracking = OrderTracking(
        order_id=order.id,
        status=status,
        remarks=f"Order moved to {status}",
    )

    db.add(tracking)

    if status == "Refunded":
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if payment is not None:
            payment.status = "Refunded"
        order.payment_status = "Refunded"

    db.commit()

    db.refresh(order)

    if status == "Shipped":

        _send_email_safely(
            order.user.email,
            "Order Shipped",
            shipped(order.user, order),
        )

    elif status == "Delivered":

        _send_email_safely(
            order.user.email,
            "Order Delivered",
            delivered(order.user, order),
        )

    elif status == "Cancelled":

        _send_email_safely(
            order.user.email,
            "Order Cancelled",
            cancelled(order.user, order),
        )

    return order


def get_order_tracking(
    db: Session,
    user: User,
    order_id: int,
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user.id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return (
        db.query(OrderTracking)
        .filter(
            OrderTracking.order_id == order_id,
        )
        .order_by(
            OrderTracking.created_at.asc(),
        )
        .all()
    )