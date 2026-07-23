from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CouponCreate(BaseModel):
    code: str
    discount_percentage: float
    expiry_date: datetime
    active: bool = True


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_percentage: float
    expiry_date: datetime
    active: bool

    class Config:
        from_attributes = True
