"""
E-commerce Extension API Routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database.database import get_db
from app.database import ecommerce_extension_model, order_model, payment_model, order_item_model, models
from app.schemas import ecommerce_extension_schema
from app.auth.oauth2 import get_current_user
from app.utils.role_checker import admin_only, user_or_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["E-commerce Extensions"])


# Addresses
@router.get("/addresses", response_model=List[ecommerce_extension_schema.AddressResponse])
async def get_user_addresses(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all addresses for current user"""
    user_or_admin(current_user)
    
    addresses = db.query(ecommerce_extension_model.Address).filter_by(user_id=current_user.id).all()
    return addresses


@router.post("/addresses", response_model=ecommerce_extension_schema.AddressResponse)
async def create_address(
    address: ecommerce_extension_schema.AddressCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new address"""
    user_or_admin(current_user)
    
    db_address = ecommerce_extension_model.Address(
        user_id=current_user.id,
        **address.dict()
    )
    
    # If this is default address, unset other defaults
    if address.is_default:
        db.query(ecommerce_extension_model.Address).filter(
            ecommerce_extension_model.Address.user_id == current_user.id,
            ecommerce_extension_model.Address.is_default == True
        ).update({"is_default": False})
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


@router.get("/addresses/{address_id}", response_model=ecommerce_extension_schema.AddressResponse)
async def get_address(
    address_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get address details"""
    user_or_admin(current_user)
    
    address = db.query(ecommerce_extension_model.Address).filter(
        ecommerce_extension_model.Address.id == address_id,
        ecommerce_extension_model.Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/addresses/{address_id}", response_model=ecommerce_extension_schema.AddressResponse)
async def update_address(
    address_id: int,
    address_update: ecommerce_extension_schema.AddressCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update address"""
    user_or_admin(current_user)
    
    address = db.query(ecommerce_extension_model.Address).filter(
        ecommerce_extension_model.Address.id == address_id,
        ecommerce_extension_model.Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, unset other defaults
    if address_update.is_default and not address.is_default:
        db.query(ecommerce_extension_model.Address).filter(
            ecommerce_extension_model.Address.user_id == current_user.id,
            ecommerce_extension_model.Address.is_default == True
        ).update({"is_default": False})
    
    for key, value in address_update.dict().items():
        setattr(address, key, value)
    
    db.commit()
    db.refresh(address)
    return address


@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete address"""
    user_or_admin(current_user)
    
    address = db.query(ecommerce_extension_model.Address).filter(
        ecommerce_extension_model.Address.id == address_id,
        ecommerce_extension_model.Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(address)
    db.commit()
    return {"message": "Address deleted"}


# Order Returns
@router.get("/orders/{order_id}/returns", response_model=List[ecommerce_extension_schema.OrderReturnResponse])
async def get_order_returns(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get returns for an order"""
    user_or_admin(current_user)
    
    # Check if user owns the order
    order = db.query(order_model.Order).filter_by(id=order_id).first()
    if not order or (order.user_id != current_user.id and current_user.role != "ADMIN"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    returns = db.query(ecommerce_extension_model.OrderReturn).filter_by(order_id=order_id).all()
    return returns


@router.post("/orders/{order_id}/returns", response_model=ecommerce_extension_schema.OrderReturnResponse)
async def create_order_return(
    order_id: int,
    return_request: ecommerce_extension_schema.OrderReturnCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order return request"""
    user_or_admin(current_user)
    
    # Check if user owns the order
    order = db.query(order_model.Order).filter_by(id=order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if order is eligible for return (delivered)
    if order.status not in ["Delivered", "Completed"]:
        raise HTTPException(status_code=400, detail="Order is not eligible for return")
    
    db_return = ecommerce_extension_model.OrderReturn(
        order_id=order_id,
        **return_request.dict()
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)
    return db_return


@router.get("/returns/{return_id}", response_model=ecommerce_extension_schema.OrderReturnResponse)
async def get_return(
    return_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get return details"""
    user_or_admin(current_user)
    
    db_return = db.query(ecommerce_extension_model.OrderReturn).filter_by(id=return_id).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Return not found")
    
    # Check access
    if db_return.order.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return db_return


@router.put("/returns/{return_id}", response_model=ecommerce_extension_schema.OrderReturnResponse)
async def update_return(
    return_id: int,
    return_update: ecommerce_extension_schema.OrderReturnUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update return (admin only)"""
    admin_only(current_user)
    
    db_return = db.query(ecommerce_extension_model.OrderReturn).filter_by(id=return_id).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Return not found")
    
    for key, value in return_update.dict(exclude_unset=True).items():
        if value is not None:
            if key == "status":
                if value == "APPROVED":
                    db_return.approved_at = datetime.utcnow()
                elif value == "REJECTED":
                    db_return.rejected_at = datetime.utcnow()
                elif value == "COMPLETED":
                    db_return.completed_at = datetime.utcnow()
            setattr(db_return, key, value)
    
    db.commit()
    db.refresh(db_return)
    return db_return


# Shipments
@router.get("/orders/{order_id}/shipments", response_model=List[ecommerce_extension_schema.ShipmentResponse])
async def get_order_shipments(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shipments for an order"""
    user_or_admin(current_user)
    
    # Check if user owns the order
    order = db.query(order_model.Order).filter_by(id=order_id).first()
    if not order or (order.user_id != current_user.id and current_user.role != "ADMIN"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    shipments = db.query(ecommerce_extension_model.Shipment).filter_by(order_id=order_id).all()
    return shipments


@router.get("/shipments/{shipment_id}", response_model=ecommerce_extension_schema.ShipmentResponse)
async def get_shipment(
    shipment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shipment details"""
    user_or_admin(current_user)
    
    shipment = db.query(ecommerce_extension_model.Shipment).filter_by(id=shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Check access
    if shipment.order.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return shipment


@router.get("/shipments/track/{tracking_number}", response_model=ecommerce_extension_schema.ShipmentResponse)
async def track_shipment(
    tracking_number: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track shipment by tracking number"""
    user_or_admin(current_user)
    
    shipment = db.query(ecommerce_extension_model.Shipment).filter_by(
        tracking_number=tracking_number
    ).first()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Check access
    if shipment.order.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return shipment


@router.put("/shipments/{shipment_id}", response_model=ecommerce_extension_schema.ShipmentResponse)
async def update_shipment(
    shipment_id: int,
    shipment_update: ecommerce_extension_schema.ShipmentUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update shipment (admin only)"""
    admin_only(current_user)
    
    shipment = db.query(ecommerce_extension_model.Shipment).filter_by(id=shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    for key, value in shipment_update.dict(exclude_unset=True).items():
        if value is not None:
            if key == "status" and value == "DELIVERED":
                shipment.actual_delivery = datetime.utcnow()
            setattr(shipment, key, value)
    
    db.commit()
    db.refresh(shipment)
    return shipment


# Shipping Methods
@router.get("/shipping-methods", response_model=List[ecommerce_extension_schema.ShippingMethodResponse])
async def get_shipping_methods(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available shipping methods"""
    user_or_admin(current_user)
    
    methods = db.query(ecommerce_extension_model.ShippingMethod).filter_by(is_active=True).all()
    return methods


@router.post("/shipping-methods", response_model=ecommerce_extension_schema.ShippingMethodResponse)
async def create_shipping_method(
    method: ecommerce_extension_schema.ShippingMethodCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create shipping method (admin only)"""
    admin_only(current_user)
    
    db_method = ecommerce_extension_model.ShippingMethod(**method.dict())
    db.add(db_method)
    db.commit()
    db.refresh(db_method)
    return db_method


# Sales Dashboard
@router.get("/dashboard/sales", response_model=ecommerce_extension_schema.SalesDashboardResponse)
async def get_sales_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sales dashboard"""
    admin_only(current_user)
    
    today = datetime.utcnow().date()
    month_start = datetime.utcnow().replace(day=1).date()
    year_start = datetime.utcnow().replace(month=1, day=1).date()

    completed_orders_query = db.query(order_model.Order).filter(order_model.Order.payment_status == "Completed")

    today_orders = db.query(func.sum(order_model.Order.total_amount)).filter(
        func.date(order_model.Order.created_at) == today,
        order_model.Order.payment_status == "Completed"
    ).scalar() or 0.0

    month_orders = db.query(func.sum(order_model.Order.total_amount)).filter(
        func.date(order_model.Order.created_at) >= month_start,
        order_model.Order.payment_status == "Completed"
    ).scalar() or 0.0

    year_orders = db.query(func.sum(order_model.Order.total_amount)).filter(
        func.date(order_model.Order.created_at) >= year_start,
        order_model.Order.payment_status == "Completed"
    ).scalar() or 0.0

    today_order_count = db.query(func.count(order_model.Order.id)).filter(
        func.date(order_model.Order.created_at) == today,
        order_model.Order.payment_status == "Completed"
    ).scalar() or 0

    month_order_count = db.query(func.count(order_model.Order.id)).filter(
        func.date(order_model.Order.created_at) >= month_start,
        order_model.Order.payment_status == "Completed"
    ).scalar() or 0

    total_customers = db.query(order_model.Order.user_id).filter(
        order_model.Order.payment_status == "Completed"
    ).distinct().count()

    avg_order_value = today_orders / today_order_count if today_order_count > 0 else 0.0

    top_selling_products = (
        db.query(
            models.Product.name,
            func.sum(order_item_model.OrderItem.quantity).label("units_sold"),
            func.sum(order_item_model.OrderItem.price_at_purchase * order_item_model.OrderItem.quantity).label("revenue"),
        )
        .join(order_item_model.OrderItem, order_item_model.OrderItem.product_id == models.Product.id)
        .group_by(models.Product.id)
        .order_by(func.sum(order_item_model.OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    recent_orders = (
        db.query(order_model.Order)
        .order_by(order_model.Order.created_at.desc())
        .limit(5)
        .all()
    )

    revenue_trend = []
    for days_back in range(6, -1, -1):
        day_start = (datetime.utcnow().date() - timedelta(days=days_back))
        revenue = db.query(func.sum(order_model.Order.total_amount)).filter(
            func.date(order_model.Order.created_at) == day_start,
            order_model.Order.payment_status == "Completed"
        ).scalar() or 0.0
        revenue_trend.append({"date": day_start.strftime("%Y-%m-%d"), "revenue": float(revenue)})

    category_distribution = (
        db.query(models.Product.category, func.sum(order_item_model.OrderItem.quantity).label("units_sold"))
        .join(order_item_model.OrderItem, order_item_model.OrderItem.product_id == models.Product.id)
        .group_by(models.Product.category)
        .order_by(func.sum(order_item_model.OrderItem.quantity).desc())
        .all()
    )

    return ecommerce_extension_schema.SalesDashboardResponse(
        total_revenue_today=float(today_orders),
        total_revenue_month=float(month_orders),
        total_revenue_year=float(year_orders),
        total_orders_today=today_order_count,
        total_orders_month=month_order_count,
        total_customers=total_customers,
        average_order_value=avg_order_value,
        top_selling_products=[
            {
                "name": item[0],
                "units_sold": int(item[1]),
                "revenue": float(item[2]),
            }
            for item in top_selling_products
        ],
        recent_orders=[
            {
                "id": order.id,
                "customer_email": order.user.email if getattr(order, "user", None) else None,
                "total_amount": float(order.total_amount),
                "payment_status": order.payment_status,
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
            for order in recent_orders
        ],
        revenue_trend=revenue_trend,
        category_distribution=[
            {"category": item[0], "units_sold": int(item[1])}
            for item in category_distribution
        ],
    )
