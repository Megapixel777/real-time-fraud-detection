from datetime import UTC, datetime
from unittest.mock import MagicMock

from fraud_detection.generator.transaction import Transaction
from fraud_detection.kafka.producer import KafkaTransactionProducer


def test_send_transaction():
    producer = KafkaTransactionProducer.__new__(KafkaTransactionProducer)

    producer.topic = "fraud-transactions"
    producer.producer = MagicMock()

    transaction = Transaction(
        transaction_id="TX-000001",
        customer_id="C-1001",
        amount=125.50,
        currency="EUR",
        country="ES",
        merchant="ONLINE_STORE",
        timestamp=datetime(2026, 9, 16, 10, 0, tzinfo=UTC),
        device_id="DEV-1001",
    )

    producer.send(transaction)

    producer.producer.send.assert_called_once()

    call = producer.producer.send.call_args

    assert call.args[0] == "fraud-transactions"
    assert call.kwargs["value"]["transaction_id"] == "TX-000001"
    assert call.kwargs["value"]["customer_id"] == "C-1001"
    assert call.kwargs["value"]["amount"] == 125.50
