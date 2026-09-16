import argparse
import time

from fraud_detection.generator.scenario import TransactionScenario
from fraud_detection.generator.scenario_generator import ScenarioGenerator
from fraud_detection.generator.transaction_generator import TransactionGenerator
from fraud_detection.kafka.producer import KafkaTransactionProducer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and publish fraud detection transactions."
    )

    parser.add_argument(
        "--scenario",
        choices=[scenario.value for scenario in TransactionScenario],
        default=TransactionScenario.NORMAL.value,
        help="Transaction scenario to generate.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Seconds between transactions.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    transaction_generator = TransactionGenerator()
    scenario_generator = ScenarioGenerator(transaction_generator)
    kafka_producer = KafkaTransactionProducer()

    scenario = TransactionScenario(args.scenario)

    try:
        while True:
            if scenario == TransactionScenario.VELOCITY_ATTACK:
                transactions = scenario_generator.generate_velocity_attack(
                    interval_seconds=int(args.interval),
                )
            elif scenario == TransactionScenario.COUNTRY_HOPPING:
                transactions = scenario_generator.generate_country_hopping(
                    interval_seconds=int(args.interval),
                )
            elif scenario == TransactionScenario.MULTI_DEVICE:
                transactions = scenario_generator.generate_multi_device(
                    interval_seconds=int(args.interval),
                )
            else:
                transactions = [
                    transaction_generator.generate(
                        scenario=scenario,
                    )
                ]

            for transaction in transactions:
                kafka_producer.send(transaction)

                print(
                    f"Sent transaction: "
                    f"{transaction.transaction_id} | "
                    f"scenario={scenario.value} | "
                    f"customer={transaction.customer_id} | "
                    f"amount={transaction.amount} | "
                    f"country={transaction.country} | "
                    f"device={transaction.device_id}"
                )

            kafka_producer.flush()

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nStopping transaction producer...")

    finally:
        kafka_producer.close()


if __name__ == "__main__":
    main()
