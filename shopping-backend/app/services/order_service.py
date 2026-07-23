from datetime import datetime
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
            or coupon.expiry_date < datetime.utcnow()
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

        asyncio.create_task(
            send_email(
                user.email,
                "Order Confirmation",
                order_confirmation(
                    user,
                    order,
                ),
            )
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

    order.status = "Cancelled"
    order.payment_status = "Refunded"

    tracking = OrderTracking(
        order_id=order.id,
        status="Cancelled",
        remarks="Order Cancelled",
    )

    db.add(tracking)

    db.commit()

    db.refresh(order)

    asyncio.create_task(
        send_email(
            user.email,
            "Order Cancelled",
            cancelled(
                user,
                order,
            ),
        )
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
        .filter(Order.id == order_id)
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    order.status = status

    tracking = OrderTracking(
        order_id=order.id,
        status=status,
        remarks=f"Order moved to {status}",
    )

    db.add(tracking)

    if status == "Delivered":
        order.payment_status = "Completed"

    elif status == "Refunded":
        order.payment_status = "Refunded"

    db.commit()

    db.refresh(order)

    if status == "Shipped":

        asyncio.create_task(
            send_email(
                order.user.email,
                "Order Shipped",
                shipped(
                    order.user,
                    order,
                ),
            )
        )

    elif status == "Delivered":

        asyncio.create_task(
            send_email(
                order.user.email,
                "Order Delivered",
                delivered(
                    order.user,
                    order,
                ),
            )
        )

    elif status == "Cancelled":

        asyncio.create_task(
            send_email(
                order.user.email,
                "Order Cancelled",
                cancelled(
                    order.user,
                    order,
                ),
            )
        )

    return order


def get_order_tracking(
    db: Session,
    order_id: int,
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
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