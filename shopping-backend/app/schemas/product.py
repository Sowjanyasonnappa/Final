from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    price: float
    stock: int