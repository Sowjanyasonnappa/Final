from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
