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

    assert all(
        transaction.customer_id == "C-1001"
        for transaction in transactions
    )

def test_velocity_attack_transactions_are_time_ordered():
    generator = ScenarioGenerator()

    transactions = generator.generate_velocity_attack(
        customer_id="C-1001",
        transaction_count=5,
        interval_seconds=20,
    )

    for previous, current in pairwise(transactions):
        assert current.timestamp > previous.timestamp