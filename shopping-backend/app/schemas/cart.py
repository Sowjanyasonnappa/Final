from typing import Optional
from pydantic import BaseModel


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    total_price: float
