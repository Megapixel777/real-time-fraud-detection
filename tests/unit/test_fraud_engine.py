from datetime import datetime, timezone

from fraud_detection.fraud.engine import FraudEngine
from fraud_detection.fraud.signals import FraudSignals
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

    signals = FraudSignals(
        high_amount=True,
        velocity_attack=False,
        country_hopping=False,
        multi_device=False,
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        signals=signals,
    )

    assert result.is_fraud is True
    assert result.fraud_score == 0.3
    assert result.fraud_reasons == ["HIGH_AMOUNT"]


def test_normal_transaction_returns_no_fraud():
    transaction = create_transaction(
        100.0,
        datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
    )

    signals = FraudSignals(
        high_amount=False,
        velocity_attack=False,
        country_hopping=False,
        multi_device=False,
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        signals=signals,
    )

    assert result.is_fraud is False
    assert result.fraud_score == 0.0
    assert result.fraud_reasons == []


def test_multiple_rules_are_combined():
    transaction = create_transaction(
        5000.0,
        datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
    )

    signals = FraudSignals(
        high_amount=True,
        velocity_attack=False,
        country_hopping=True,
        multi_device=True,
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        signals=signals,
    )

    assert result.is_fraud is True
    assert result.fraud_score == 0.7
    assert result.fraud_reasons == [
        "HIGH_AMOUNT",
        "COUNTRY_HOPPING",
        "MULTI_DEVICE",
    ]


def test_fraud_engine_returns_structured_result():
    transaction = create_transaction(
        7500.0,
        datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
    )

    signals = FraudSignals(
        high_amount=True,
        velocity_attack=False,
        country_hopping=False,
        multi_device=False,
    )

    result = FraudEngine().evaluate(
        transaction=transaction,
        signals=signals,
    )

    assert result.transaction_id == "TX-000001"
    assert result.customer_id == "C-1001"
    assert result.amount == 7500.0
    assert result.is_fraud is True
    assert result.fraud_score == 0.30
    assert result.fraud_reasons == ["HIGH_AMOUNT"]