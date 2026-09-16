import json

from kafka import KafkaProducer

from fraud_detection.generator.transaction import Transaction


class KafkaTransactionProducer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "fraud-transactions",
    ):
        self.topic = topic

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=self._serialize,
        )

    @staticmethod
    def _serialize(value: dict) -> bytes:
        return json.dumps(value).encode("utf-8")

    def send(self, transaction: Transaction) -> None:
        self.producer.send(
            self.topic,
            value=transaction.model_dump(mode="json"),
        )

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()
