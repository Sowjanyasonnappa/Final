from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.oauth2 import admin_required

from app.database.order_model import Order
from app.database.models import Product
from app.database.user_model import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    total_users = db.query(User).count()

    total_products = db.query(Product).count()

    total_orders = db.query(Order).count()

    orders = db.query(Order).all()

    revenue = sum(
        order.total_amount
        for order in orders
    )

    low_stock_products = (
        db.query(Product)
        .filter(Product.stock < 10)
        .all()
    )

    recent_orders = (
        db.query(Order)
        .order_by(Order.id.desc())
        .limit(5)
        .all()
    )

    return {
        "admin": current_user.email,
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "revenue": revenue,
        "low_stock_products": low_stock_products,
        "recent_orders": recent_orders,
    }