from datetime import UTC, datetime

from fraud_detection.generator.transaction import Transaction


def test_transaction_creation():
    transaction = Transaction(
        transaction_id="TX-849201",
        customer_id="C-1029",
        amount=1250.50,
        currency="EUR",
        country="ES",
        merchant="ONLINE_STORE",
        timestamp=datetime.now(UTC),
        device_id="DEV-8831",
    )

    assert transaction.transaction_id == "TX-849201"
    assert transaction.customer_id == "C-1029"
    assert transaction.amount == 1250.50
    assert transaction.currency == "EUR"
