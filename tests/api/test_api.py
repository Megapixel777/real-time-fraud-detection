from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import psycopg
from fastapi.testclient import TestClient

from fraud_detection.api.main import app

client = TestClient(app)


TRANSACTION = {
    "transaction_id": "TX-TEST-001",
    "customer_id": "CUSTOMER-001",
    "timestamp": datetime(2026, 9, 21, 10, 0, 0, tzinfo=UTC),
    "amount": Decimal("125.50"),
    "currency": "EUR",
    "country": "ES",
    "merchant": "Test Merchant",
    "device_id": "DEVICE-001",
    "is_fraud": True,
    "fraud_score": Decimal("0.70"),
    "fraud_reasons": [
        "VELOCITY_ATTACK",
        "COUNTRY_HOPPING",
    ],
    "created_at": datetime(2026, 9, 21, 10, 0, 1, tzinfo=UTC),
}


def create_mock_connection(rows=None, row=None):
    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchall.return_value = rows or []
    cursor.fetchone.return_value = row

    connection.cursor.return_value.__enter__.return_value = cursor
    connection.__enter__.return_value = connection

    return connection


def test_health_database_connected():
    connection = create_mock_connection()

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }


def test_health_database_unavailable():
    error = psycopg.OperationalError("Database unavailable")

    with patch(
        "fraud_detection.api.main.get_connection",
        side_effect=error,
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "unhealthy",
        "database": "unavailable",
    }


def test_get_transactions():
    connection = create_mock_connection(rows=[TRANSACTION])

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["transaction_id"] == "TX-TEST-001"
    assert data[0]["is_fraud"] is True
    assert data[0]["fraud_score"] == "0.70"


def test_get_transactions_with_fraud_filter():
    connection = create_mock_connection(rows=[TRANSACTION])

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions?is_fraud=true")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_fraud"] is True


def test_get_transactions_with_country_filter():
    connection = create_mock_connection(rows=[TRANSACTION])

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions?country=es")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["country"] == "ES"


def test_get_transactions_with_min_score():
    connection = create_mock_connection(rows=[TRANSACTION])

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions?min_score=0.5")

    assert response.status_code == 200
    assert response.json()[0]["fraud_score"] == "0.70"


def test_get_transaction():
    connection = create_mock_connection(row=TRANSACTION)

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions/TX-TEST-001")

    assert response.status_code == 200
    assert response.json()["transaction_id"] == "TX-TEST-001"


def test_get_transaction_not_found():
    connection = create_mock_connection(row=None)

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/transactions/DOES-NOT-EXIST")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Transaction 'DOES-NOT-EXIST' not found"
    )


def test_get_fraud_transactions():
    connection = create_mock_connection(rows=[TRANSACTION])

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get("/fraud/transactions")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_fraud"] is True


def test_investigate_fraudulent_transaction():
    connection = create_mock_connection(row=TRANSACTION)

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get(
            "/fraud/investigate/TX-TEST-001"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["fraud_detected"] is True
    assert data["fraud_score"] == "0.70"
    assert data["risk_level"] == "HIGH"
    assert data["triggered_rules"] == [
        "VELOCITY_ATTACK",
        "COUNTRY_HOPPING",
    ]


def test_investigate_transaction_not_found():
    connection = create_mock_connection(row=None)

    with patch(
        "fraud_detection.api.main.get_connection",
        return_value=connection,
    ):
        response = client.get(
            "/fraud/investigate/DOES-NOT-EXIST"
        )

    assert response.status_code == 404