from datetime import datetime, timedelta, timezone

from fraud_detection.fraud.engine import FraudEngine
from fraud_detection.generator.transaction import Transaction


def create_transaction(
    amount: float,
    timestamp: datetime,
    country: str = "ES",
    device_id: str = "DEV-1001",
) -> Transaction:
    return Transaction(
        transaction_id="TX-000001",
        customer_id="C-1001",
        amount=amount,
        currency="EUR",
        country=country,
        merchant="ONLINE_STORE",
        timestamp=timestamp,
        device_id=device_id,
    )


def test_high_amount_returns_fraud():
    transaction = create_transaction(
        5000.0,
        datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        transactions=[transaction],
    )

    assert result.is_fraud is True
    assert result.fraud_score == 0.3
    assert result.fraud_reasons == ["HIGH_AMOUNT"]


def test_normal_transaction_returns_no_fraud():
    transaction = create_transaction(
        100.0,
        datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        transactions=[transaction],
    )

    assert result.is_fraud is False
    assert result.fraud_score == 0.0
    assert result.fraud_reasons == []


def test_multiple_rules_are_combined():
    base_timestamp = datetime(
        2026,
        9,
        18,
        18,
        0,
        tzinfo=timezone.utc,
    )

    transactions = [
        create_transaction(
            5000.0,
            base_timestamp + timedelta(seconds=0),
            country="ES",
            device_id="DEV-1001",
        ),
        create_transaction(
            100.0,
            base_timestamp + timedelta(seconds=20),
            country="FR",
            device_id="DEV-2001",
        ),
        create_transaction(
            100.0,
            base_timestamp + timedelta(seconds=40),
            country="DE",
            device_id="DEV-3001",
        ),
    ]

    result = FraudEngine().evaluate(
        transaction=transactions[0],
        transactions=transactions,
    )

    assert result.is_fraud is True
    assert result.fraud_score == 0.7
    assert result.fraud_reasons == [
        "HIGH_AMOUNT",
        "COUNTRY_HOPPING",
        "MULTI_DEVICE",
    ]