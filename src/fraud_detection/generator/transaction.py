from datetime import datetime

from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    country: str
    merchant: str
    timestamp: datetime
    device_id: str