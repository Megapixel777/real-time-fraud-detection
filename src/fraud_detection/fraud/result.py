from datetime import datetime

from pydantic import BaseModel


class FraudDetectionResult(BaseModel):
    transaction_id: str
    customer_id: str
    timestamp: datetime
    amount: float
    currency: str
    country: str
    merchant: str
    device_id: str
    is_fraud: bool
    fraud_score: float
    fraud_reasons: list[str]