"""
E-commerce Extension Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Address Schemas
class AddressBase(BaseModel):
    title: str = Field(..., description="Address title (Home, Work, etc.)")
    full_name: str
    phone: str
    email: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    address_type: str = "billing"


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Return Schemas
class OrderReturnBase(BaseModel):
    reason: str
    description: str
    quantity: int = 1


class OrderReturnCreate(OrderReturnBase):
    pass


class OrderReturnResponse(OrderReturnBase):
    id: int
    order_id: int
    order_item_id: Optional[int]
    status: str
    refund_amount: Optional[float]
    requested_at: datetime
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    rejected_at: Optional[datetime]
    tracking_number: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderReturnUpdate(BaseModel):
    status: Optional[str] = None
    refund_amount: Optional[float] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


# Refund Schemas
class RefundBase(BaseModel):
    amount: float
    method: str = "ORIGINAL"


class RefundCreate(RefundBase):
    pass


class RefundResponse(RefundBase):
    id: int
    order_return_id: int
    payment_id: Optional[int]
    status: str
    gateway_refund_id: Optional[str]
    initiated_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Shipping Method Schemas
class ShippingMethodBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_cost: float
    cost_per_item: float = 0
    estimated_days: int


class ShippingMethodCreate(ShippingMethodBase):
    pass


class ShippingMethodResponse(ShippingMethodBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Shipment Schemas
class ShipmentBase(BaseModel):
    carrier: str
    to_address: Dict[str, Any]
    shipping_cost: float
    insurance_cost: float = 0


class ShipmentCreate(ShipmentBase):
    shipping_method_id: int


class ShipmentResponse(ShipmentBase):
    id: int
    order_id: int
    shipping_method_id: int
    tracking_number: Optional[str]
    status: str
    from_address: Optional[Dict[str, Any]]
    ship_date: Optional[datetime]
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    events: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShipmentUpdate(BaseModel):
    status: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None


# Sales Metrics Schemas
class SalesMetricResponse(BaseModel):
    id: int
    date: datetime
    year: int
    month: int
    day: int
    total_orders: int
    total_revenue: float
    average_order_value: float
    total_items_sold: int
    unique_customers: int
    top_category: Optional[str]
    new_customers: int
    returning_customers: int
    total_returns: int
    total_refunds: float
    created_at: datetime

    class Config:
        from_attributes = True


# Product View History Schemas
class ProductViewHistoryResponse(BaseModel):
    id: int
    product_id: int
    view_count: int
    last_viewed: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Product Recommendation Schemas
class ProductRecommendationBase(BaseModel):
    reason: Optional[str] = None
    recommendation_type: str = "SIMILAR"


class ProductRecommendationResponse(ProductRecommendationBase):
    id: int
    product_id: int
    score: Optional[float]
    ai_generated: bool
    ai_model: Optional[str]
    clicked: bool
    clicked_at: Optional[datetime]
    purchased: bool
    purchased_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Customer Segment Schemas
class CustomerSegmentResponse(BaseModel):
    id: int
    total_purchases: int
    total_spent: float
    average_order_value: float
    last_purchase_date: Optional[datetime]
    days_since_purchase: Optional[int]
    segment: str
    lifetime_value: float
    churn_risk: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class SalesDashboardResponse(BaseModel):
    total_revenue_today: float
    total_revenue_month: float
    total_revenue_year: float
    total_orders_today: int
    total_orders_month: int
    total_customers: int
    average_order_value: float
    top_selling_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    category_distribution: List[Dict[str, Any]]


class CustomerAnalyticsResponse(BaseModel):
    total_customers: int
    new_customers_month: int
    returning_customers: int
    churned_customers: int
    customer_lifetime_value: float
    average_customer_lifetime_value: float
    customer_segments: Dict[str, int]
    top_customers: List[Dict[str, Any]]


# Analytics Filters
class SalesReportFilter(BaseModel):
    start_date: datetime
    end_date: datetime
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    top_n: int = 10


class CustomerReportFilter(BaseModel):
    segment: Optional[str] = None
    min_purchases: int = 0
    min_lifetime_value: float = 0
    top_n: int = 20
