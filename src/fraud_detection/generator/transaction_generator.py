import random
from datetime import UTC, datetime
from typing import ClassVar

from fraud_detection.generator.scenario import TransactionScenario
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

    SUSPICIOUS_MERCHANTS: ClassVar[list[str]] = [
        "CRYPTO_EXCHANGE",
        "UNKNOWN_MERCHANT",
        "UNREGULATED_BROKER",
    ]

    def generate(
        self,
        scenario: TransactionScenario = TransactionScenario.NORMAL,
        customer_id: str | None = None,
        timestamp: datetime | None = None,
        country: str | None = None,
        device_id: str | None = None,
    ) -> Transaction:
        merchant = (
            random.choice(self.SUSPICIOUS_MERCHANTS)
            if scenario == TransactionScenario.SUSPICIOUS_MERCHANT
            else random.choice(self.MERCHANTS)
        )

        return Transaction(
            transaction_id=self._generate_transaction_id(),
            customer_id=customer_id or self._generate_customer_id(),
            amount=self._generate_amount(scenario),
            currency=random.choice(self.CURRENCIES),
            country=country or random.choice(self.COUNTRIES),
            merchant=merchant,
            timestamp=timestamp or datetime.now(UTC),
            device_id=device_id or self._generate_device_id(),
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
    def _generate_amount(scenario: TransactionScenario) -> float:
        if scenario == TransactionScenario.HIGH_AMOUNT:
            return round(random.uniform(5000, 20000), 2)

        return round(random.uniform(1, 500), 2)
