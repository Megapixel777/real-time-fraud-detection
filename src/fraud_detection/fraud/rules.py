from datetime import timedelta

from fraud_detection.generator.transaction import Transaction

HIGH_AMOUNT_THRESHOLD = 5000.0


def is_high_amount(transaction: Transaction) -> bool:
    return transaction.amount >= HIGH_AMOUNT_THRESHOLD


def is_velocity_attack(
    transactions: list[Transaction],
    max_transactions: int = 5,
    window_seconds: int = 60,
) -> bool:
    if len(transactions) < max_transactions:
        return False

    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.timestamp,
    )

    window = timedelta(seconds=window_seconds)

    for index in range(len(sorted_transactions) - max_transactions + 1):
        first = sorted_transactions[index]
        last = sorted_transactions[index + max_transactions - 1]

        if last.timestamp - first.timestamp <= window:
            return True

    return False

def is_country_hopping(
    transactions: list[Transaction],
    min_countries: int = 3,
    window_seconds: int = 60,
) -> bool:
    if len(transactions) < min_countries:
        return False

    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.timestamp,
    )

    window = timedelta(seconds=window_seconds)

    for index, first in enumerate(sorted_transactions):
        countries = set()

        for transaction in sorted_transactions[index:]:
            if transaction.timestamp - first.timestamp > window:
                break

            countries.add(transaction.country)

            if len(countries) >= min_countries:
                return True

    return False

def is_multi_device(
    transactions: list[Transaction],
    min_devices: int = 3,
    window_seconds: int = 60,
) -> bool:
    if len(transactions) < min_devices:
        return False

    sorted_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.timestamp,
    )

    window = timedelta(seconds=window_seconds)

    for index, first in enumerate(sorted_transactions):
        devices = set()

        for transaction in sorted_transactions[index:]:
            if transaction.timestamp - first.timestamp > window:
                break

            devices.add(transaction.device_id)

            if len(devices) >= min_devices:
                return True

    return False