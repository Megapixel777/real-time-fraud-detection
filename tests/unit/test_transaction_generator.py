from datetime import datetime, timezone

from fraud_detection.generator.scenario import TransactionScenario
from fraud_detection.generator.transaction import Transaction
from fraud_detection.generator.transaction_generator import TransactionGenerator


def test_generate_returns_transaction():
    generator = TransactionGenerator()

    transaction = generator.generate()

    assert isinstance(transaction, Transaction)


def test_generated_amount_is_valid():
    generator = TransactionGenerator()

    transaction = generator.generate()

    assert 1 <= transaction.amount <= 500


def test_generated_transaction_has_expected_ids():
    generator = TransactionGenerator()

    transaction = generator.generate()

    assert transaction.transaction_id.startswith("TX-")
    assert transaction.customer_id.startswith("C-")
    assert transaction.device_id.startswith("DEV-")


def test_high_amount_scenario():
    generator = TransactionGenerator()

    transaction = generator.generate(TransactionScenario.HIGH_AMOUNT)

    assert 5000 <= transaction.amount <= 20000

def test_suspicious_merchant_scenario():
    generator = TransactionGenerator()

    transaction = generator.generate(
        TransactionScenario.SUSPICIOUS_MERCHANT
    )

    assert transaction.merchant in TransactionGenerator.SUSPICIOUS_MERCHANTS

def test_generate_with_custom_customer_and_timestamp():
    generator = TransactionGenerator()

    timestamp = datetime(2026, 9, 14, 18, 0, 0, tzinfo=timezone.utc)

    transaction = generator.generate(
        customer_id="C-1001",
        timestamp=timestamp,
    )

    assert transaction.customer_id == "C-1001"
    assert transaction.timestamp == timestamp