from enum import Enum


class TransactionScenario(str, Enum):
    NORMAL = "normal"
    HIGH_AMOUNT = "high_amount"
    SUSPICIOUS_MERCHANT = "suspicious_merchant"