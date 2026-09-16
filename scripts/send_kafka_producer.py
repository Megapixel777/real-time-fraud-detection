from fraud_detection.generator.transaction_generator import TransactionGenerator
from fraud_detection.kafka.producer import KafkaTransactionProducer


def main() -> None:
    transaction_generator = TransactionGenerator()
    kafka_producer = KafkaTransactionProducer()

    transaction = transaction_generator.generate(
        customer_id="C-1001",
    )

    kafka_producer.send(transaction)
    kafka_producer.flush()
    kafka_producer.close()

    print(f"Transaction sent: {transaction.transaction_id}")


if __name__ == "__main__":
    main()
