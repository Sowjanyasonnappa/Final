from pydantic import BaseModel


class PaymentRequest(BaseModel):
    payment_method: str


class PaymentResponse(BaseModel):
    payment_id: int
    transaction_id: str
    payment_method: str
    amount: float
    status: str

    class Config:
        from_attributes = True