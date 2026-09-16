from itertools import pairwise

from fraud_detection.generator.scenario_generator import ScenarioGenerator


def test_generate_velocity_attack():
    generator = ScenarioGenerator()

    transactions = generator.generate_velocity_attack(
        customer_id="C-1001",
        transaction_count=5,
        interval_seconds=20,
    )

    assert len(transactions) == 5

    assert all(transaction.customer_id == "C-1001" for transaction in transactions)


def test_velocity_attack_transactions_are_time_ordered():
    generator = ScenarioGenerator()

    transactions = generator.generate_velocity_attack(
        customer_id="C-1001",
        transaction_count=5,
        interval_seconds=20,
    )

    for previous, current in pairwise(transactions):
        assert current.timestamp > previous.timestamp


def test_generate_country_hopping():
    generator = ScenarioGenerator()

    countries = ["ES", "FR", "DE", "IT", "GB"]

    transactions = generator.generate_country_hopping(
        customer_id="C-1001",
        countries=countries,
        interval_seconds=20,
    )

    assert len(transactions) == 5

    assert all(transaction.customer_id == "C-1001" for transaction in transactions)

    assert [transaction.country for transaction in transactions] == countries


def test_country_hopping_respects_interval():
    generator = ScenarioGenerator()

    transactions = generator.generate_country_hopping(
        customer_id="C-1001",
        countries=["ES", "FR", "DE"],
        interval_seconds=30,
    )

    for previous, current in pairwise(transactions):
        assert (current.timestamp - previous.timestamp).total_seconds() == 30


def test_generate_multi_device():
    generator = ScenarioGenerator()

    device_ids = [
        "DEV-1001",
        "DEV-2001",
        "DEV-3001",
        "DEV-4001",
    ]

    transactions = generator.generate_multi_device(
        customer_id="C-1001",
        device_ids=device_ids,
        interval_seconds=20,
    )

    assert len(transactions) == 4

    assert all(transaction.customer_id == "C-1001" for transaction in transactions)

    assert [transaction.device_id for transaction in transactions] == device_ids


def test_multi_device_respects_interval():
    generator = ScenarioGenerator()

    transactions = generator.generate_multi_device(
        customer_id="C-1001",
        device_ids=["DEV-1", "DEV-2", "DEV-3"],
        interval_seconds=30,
    )

    for previous, current in pairwise(transactions):
        assert (current.timestamp - previous.timestamp).total_seconds() == 30
