from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    transaction_id: str
    customer_id: str
    timestamp: datetime
    amount: Decimal
    currency: str
    country: str
    merchant: str
    device_id: str
    is_fraud: bool
    fraud_score: Decimal
    fraud_reasons: list[str]
    created_at: datetime