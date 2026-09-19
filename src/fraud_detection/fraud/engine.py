from typing import ClassVar

from pydantic import BaseModel

from fraud_detection.fraud.rules import (
    is_country_hopping,
    is_high_amount,
    is_multi_device,
    is_velocity_attack,
)
from fraud_detection.generator.transaction import Transaction


class FraudResult(BaseModel):
    is_fraud: bool
    fraud_score: float
    fraud_reasons: list[str]


class FraudEngine:
    RULE_WEIGHTS: ClassVar[dict[str, float]] = {
        "HIGH_AMOUNT": 0.30,
        "VELOCITY_ATTACK": 0.30,
        "COUNTRY_HOPPING": 0.20,
        "MULTI_DEVICE": 0.20,
    }

    def evaluate(
        self,
        transaction: Transaction,
        transactions: list[Transaction],
    ) -> FraudResult:
        reasons = []

        if is_high_amount(transaction):
            reasons.append("HIGH_AMOUNT")

        if is_velocity_attack(transactions):
            reasons.append("VELOCITY_ATTACK")

        if is_country_hopping(transactions):
            reasons.append("COUNTRY_HOPPING")

        if is_multi_device(transactions):
            reasons.append("MULTI_DEVICE")

        fraud_score = min(
            sum(self.RULE_WEIGHTS[reason] for reason in reasons),
            1.0,
        )

        return FraudResult(
            is_fraud=fraud_score > 0,
            fraud_score=fraud_score,
            fraud_reasons=reasons,
        )