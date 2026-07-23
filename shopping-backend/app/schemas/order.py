from typing import Optional
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    shipping_address: str
    coupon_code: Optional[str] = None


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    payment_status: str
    shipping_address: Optional[str] = None
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True
