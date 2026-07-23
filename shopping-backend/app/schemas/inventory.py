from pydantic import BaseModel


class StockUpdate(BaseModel):

    stock: int

    remarks: str | None = None