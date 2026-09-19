from typing import ClassVar

from fraud_detection.fraud.result import FraudDetectionResult
from fraud_detection.fraud.signals import FraudSignals
from fraud_detection.generator.transaction import Transaction


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
        signals: FraudSignals,
    ) -> FraudDetectionResult:
        reasons: list[str] = []

        if signals.high_amount:
            reasons.append("HIGH_AMOUNT")

        if signals.velocity_attack:
            reasons.append("VELOCITY_ATTACK")

        if signals.country_hopping:
            reasons.append("COUNTRY_HOPPING")

        if signals.multi_device:
            reasons.append("MULTI_DEVICE")

        fraud_score = min(
            sum(self.RULE_WEIGHTS[reason] for reason in reasons),
            1.0,
        )

        return FraudDetectionResult(
            transaction_id=transaction.transaction_id,
            customer_id=transaction.customer_id,
            timestamp=transaction.timestamp,
            amount=transaction.amount,
            currency=transaction.currency,
            country=transaction.country,
            merchant=transaction.merchant,
            device_id=transaction.device_id,
            is_fraud=fraud_score > 0,
            fraud_score=fraud_score,
            fraud_reasons=reasons,
        )