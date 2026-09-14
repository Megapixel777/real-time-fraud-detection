import random
from datetime import datetime, timezone
from typing import ClassVar

from fraud_detection.generator.transaction import Transaction


class TransactionGenerator:
    CURRENCIES: ClassVar[list[str]] = ["EUR", "USD", "GBP"]

    COUNTRIES: ClassVar[list[str]] = [
        "ES",
        "FR",
        "DE",
        "IT",
        "PT",
        "GB",
        "US",
    ]

    MERCHANTS: ClassVar[list[str]] = [
        "SUPERMARKET",
        "RESTAURANT",
        "GAS_STATION",
        "ONLINE_STORE",
        "ELECTRONICS",
        "TRAVEL",
    ]

    def generate(self) -> Transaction:
        return Transaction(
            transaction_id=self._generate_transaction_id(),
            customer_id=self._generate_customer_id(),
            amount=self._generate_amount(),
            currency=random.choice(self.CURRENCIES),
            country=random.choice(self.COUNTRIES),
            merchant=random.choice(self.MERCHANTS),
            timestamp=datetime.now(timezone.utc),
            device_id=self._generate_device_id(),
        )

    @staticmethod
    def _generate_transaction_id() -> str:
        return f"TX-{random.randint(100000, 999999)}"

    @staticmethod
    def _generate_customer_id() -> str:
        return f"C-{random.randint(1000, 9999)}"

    @staticmethod
    def _generate_device_id() -> str:
        return f"DEV-{random.randint(1000, 9999)}"

    @staticmethod
    def _generate_amount() -> float:
        return round(random.uniform(1, 500), 2)