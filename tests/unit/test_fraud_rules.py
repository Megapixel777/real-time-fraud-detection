from datetime import datetime, timedelta, timezone

from fraud_detection.fraud.rules import (
    is_country_hopping,
    is_high_amount,
    is_multi_device,
    is_velocity_attack,
)
from fraud_detection.generator.transaction import Transaction


def create_transaction(
    amount: float,
    timestamp: datetime | None = None,
) -> Transaction:
    return Transaction(
        transaction_id="TX-000001",
        customer_id="C-1001",
        amount=amount,
        currency="EUR",
        country="ES",
        merchant="ONLINE_STORE",
        timestamp=timestamp
        or datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc),
        device_id="DEV-1001",
    )


def test_high_amount_is_detected():
    transaction = create_transaction(5000.0)

    assert is_high_amount(transaction) is True


def test_normal_amount_is_not_high_amount():
    transaction = create_transaction(4999.99)

    assert is_high_amount(transaction) is False


def test_velocity_attack_is_detected():
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
            100.0,
            base_timestamp + timedelta(seconds=0),
        ),
        create_transaction(
            120.0,
            base_timestamp + timedelta(seconds=10),
        ),
        create_transaction(
            80.0,
            base_timestamp + timedelta(seconds=20),
        ),
        create_transaction(
            200.0,
            base_timestamp + timedelta(seconds=30),
        ),
        create_transaction(
            150.0,
            base_timestamp + timedelta(seconds=40),
        ),
    ]

    assert is_velocity_attack(transactions) is True

def test_country_hopping_is_detected():
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
            100.0,
            base_timestamp + timedelta(seconds=0),
        ),
        create_transaction(
            120.0,
            base_timestamp + timedelta(seconds=20),
        ),
        create_transaction(
            80.0,
            base_timestamp + timedelta(seconds=40),
        ),
    ]

    transactions[0].country = "ES"
    transactions[1].country = "FR"
    transactions[2].country = "DE"

    assert is_country_hopping(transactions) is True


def test_country_hopping_is_not_detected_with_two_countries():
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
            100.0,
            base_timestamp + timedelta(seconds=0),
        ),
        create_transaction(
            120.0,
            base_timestamp + timedelta(seconds=20),
        ),
        create_transaction(
            80.0,
            base_timestamp + timedelta(seconds=40),
        ),
    ]

    transactions[0].country = "ES"
    transactions[1].country = "FR"
    transactions[2].country = "ES"

    assert is_country_hopping(transactions) is False

def test_multi_device_is_detected():
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
            100.0,
            base_timestamp + timedelta(seconds=0),
        ),
        create_transaction(
            120.0,
            base_timestamp + timedelta(seconds=20),
        ),
        create_transaction(
            80.0,
            base_timestamp + timedelta(seconds=40),
        ),
    ]

    transactions[0].device_id = "DEV-1001"
    transactions[1].device_id = "DEV-2001"
    transactions[2].device_id = "DEV-3001"

    assert is_multi_device(transactions) is True


def test_multi_device_is_not_detected_with_two_devices():
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
            100.0,
            base_timestamp + timedelta(seconds=0),
        ),
        create_transaction(
            120.0,
            base_timestamp + timedelta(seconds=20),
        ),
        create_transaction(
            80.0,
            base_timestamp + timedelta(seconds=40),
        ),
    ]

    transactions[0].device_id = "DEV-1001"
    transactions[1].device_id = "DEV-2001"
    transactions[2].device_id = "DEV-1001"

    assert is_multi_device(transactions) is False