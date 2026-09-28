from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)