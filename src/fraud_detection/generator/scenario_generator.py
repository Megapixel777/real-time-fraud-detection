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

    def generate_country_hopping(
        self,
        customer_id: str = "C-1001",
        countries: list[str] | None = None,
        interval_seconds: int = 20,
    ) -> list[Transaction]:
        countries = countries or ["ES", "FR", "DE", "IT", "GB"]

        start_time = datetime.now(timezone.utc)

        transactions = []

        for i, country in enumerate(countries):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)

            transaction = self.transaction_generator.generate(
                customer_id=customer_id,
                timestamp=timestamp,
            )

            transaction.country = country
            transactions.append(transaction)

        return transactions

    def generate_multi_device(
        self,
        customer_id: str = "C-1001",
        device_ids: list[str] | None = None,
        interval_seconds: int = 20,
    ) -> list[Transaction]:
        device_ids = device_ids or [
            "DEV-1001",
            "DEV-2001",
            "DEV-3001",
            "DEV-4001",
            "DEV-5001",
        ]

        start_time = datetime.now(timezone.utc)

        transactions = []

        for i, device_id in enumerate(device_ids):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)

            transaction = self.transaction_generator.generate(
                customer_id=customer_id,
                timestamp=timestamp,
                device_id=device_id,
            )

            transactions.append(transaction)

        return transactions