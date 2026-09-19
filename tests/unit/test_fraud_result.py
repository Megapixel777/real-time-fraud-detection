import pytest
from pydantic import ValidationError

from fraud_detection.fraud.result import FraudDetectionResult


def test_valid_fraud_detection_result():
    result = FraudDetectionResult(
        transaction_id="TX-123456",
        customer_id="C-1001",
        timestamp="2026-09-19T10:00:00+00:00",
        amount=7500.50,
        currency="EUR",
        country="ES",
        merchant="ONLINE_STORE",
        device_id="DEV-1001",
        is_fraud=True,
        fraud_score=0.8,
        fraud_reasons=["HIGH_AMOUNT", "VELOCITY_ATTACK"],
    )

    assert result.transaction_id == "TX-123456"
    assert result.customer_id == "C-1001"
    assert result.is_fraud is True
    assert result.fraud_score == 0.8
    assert result.fraud_reasons == ["HIGH_AMOUNT", "VELOCITY_ATTACK"]


def test_fraud_detection_result_without_reasons():
    result = FraudDetectionResult(
        transaction_id="TX-123456",
        customer_id="C-1001",
        timestamp="2026-09-19T10:00:00+00:00",
        amount=100.0,
        currency="EUR",
        country="ES",
        merchant="SUPERMARKET",
        device_id="DEV-1001",
        is_fraud=False,
        fraud_score=0.0,
        fraud_reasons=[],
    )

    assert result.is_fraud is False
    assert result.fraud_score == 0.0
    assert result.fraud_reasons == []


def test_missing_required_field_is_rejected():
    with pytest.raises(ValidationError):
        FraudDetectionResult(
            transaction_id="TX-123456",
            customer_id="C-1001",
            timestamp="2026-09-19T10:00:00+00:00",
            amount=100.0,
            currency="EUR",
            country="ES",
            merchant="SUPERMARKET",
            device_id="DEV-1001",
            is_fraud=True,
            fraud_score=0.5,
        )