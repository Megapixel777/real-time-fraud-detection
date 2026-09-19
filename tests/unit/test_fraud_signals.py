from fraud_detection.fraud.signals import FraudSignals


def test_fraud_signals():
    signals = FraudSignals(
        high_amount=True,
        velocity_attack=True,
        country_hopping=False,
        multi_device=True,
    )

    assert signals.high_amount is True
    assert signals.velocity_attack is True
    assert signals.country_hopping is False
    assert signals.multi_device is True