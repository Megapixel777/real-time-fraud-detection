from datetime import datetime, timedelta, timezone

from fraud_detection.generator.transaction import Transaction
from fraud_detection.generator.transaction_generator import TransactionGenerator


class ScenarioGenerator:
    def __init__(self, transaction_generator: TransactionGenerator | None = None):
        self.transaction_generator = transaction_generator or TransactionGenerator()

    def generate_velocity_attack(
        self,
        customer_id: str = "C-1001",
        transaction_count: int = 5,
        interval_seconds: int = 20,
    ) -> list[Transaction]:
        start_time = datetime.now(timezone.utc)

        transactions = []

        for i in range(transaction_count):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)

            transaction = self.transaction_generator.generate(
                customer_id=customer_id,
                timestamp=timestamp,
            )

            transactions.append(transaction)

        return transactions