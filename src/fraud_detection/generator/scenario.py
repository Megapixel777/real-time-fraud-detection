from enum import Enum


class TransactionScenario(str, Enum):
    NORMAL = "normal"
    HIGH_AMOUNT = "high_amount"
    SUSPICIOUS_MERCHANT = "suspicious_merchant"
    VELOCITY_ATTACK = "velocity_attack"
    COUNTRY_HOPPING = "country_hopping"
    MULTI_DEVICE = "multi_device"