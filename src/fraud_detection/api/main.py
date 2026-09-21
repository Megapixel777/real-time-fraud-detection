import psycopg
from fastapi import FastAPI, HTTPException, Query

from fraud_detection.api.database import get_connection
from fraud_detection.api.models import (
    FraudInvestigationResponse,
    TransactionResponse,
)

app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for querying fraud detection transactions.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with get_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return {"status": "healthy", "database": "connected"}

    except psycopg.Error:
        return {"status": "unhealthy", "database": "unavailable"}


@app.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
def get_transactions(
    limit: int = Query(default=50, ge=1, le=500),
    is_fraud: bool | None = None,
    country: str | None = Query(default=None, min_length=2, max_length=2),
    min_score: float | None = Query(default=None, ge=0.0, le=1.0),
) -> list[TransactionResponse]:
    query = """
        SELECT
            transaction_id,
            customer_id,
            timestamp,
            amount,
            currency,
            country,
            merchant,
            device_id,
            is_fraud,
            fraud_score,
            fraud_reasons,
            created_at
        FROM fraud_transactions
        WHERE 1 = 1
    """

    params: list[object] = []

    if is_fraud is not None:
        query += " AND is_fraud = %s"
        params.append(is_fraud)

    if country is not None:
        query += " AND country = %s"
        params.append(country.upper())

    if min_score is not None:
        query += " AND fraud_score >= %s"
        params.append(min_score)

    query += """
        ORDER BY timestamp DESC
        LIMIT %s
    """
    params.append(limit)

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return rows


@app.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(transaction_id: str) -> TransactionResponse:
    query = """
        SELECT
            transaction_id,
            customer_id,
            timestamp,
            amount,
            currency,
            country,
            merchant,
            device_id,
            is_fraud,
            fraud_score,
            fraud_reasons,
            created_at
        FROM fraud_transactions
        WHERE transaction_id = %s
    """

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction '{transaction_id}' not found",
        )

    return row


@app.get(
    "/fraud/transactions",
    response_model=list[TransactionResponse],
)
def get_fraud_transactions(
    limit: int = Query(default=50, ge=1, le=500),
) -> list[TransactionResponse]:
    query = """
        SELECT
            transaction_id,
            customer_id,
            timestamp,
            amount,
            currency,
            country,
            merchant,
            device_id,
            is_fraud,
            fraud_score,
            fraud_reasons,
            created_at
        FROM fraud_transactions
        WHERE is_fraud = TRUE
        ORDER BY timestamp DESC
        LIMIT %s
    """

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

    return rows


@app.get(
    "/fraud/investigate/{transaction_id}",
    response_model=FraudInvestigationResponse,
)
def investigate_transaction(
    transaction_id: str,
) -> FraudInvestigationResponse:
    query = """
        SELECT
            transaction_id,
            customer_id,
            timestamp,
            amount,
            currency,
            country,
            merchant,
            device_id,
            is_fraud,
            fraud_score,
            fraud_reasons,
            created_at
        FROM fraud_transactions
        WHERE transaction_id = %s
    """

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction '{transaction_id}' not found",
        )

    score = float(row["fraud_score"])

    if score == 0:
        risk_level = "LOW"
    elif score < 0.5:
        risk_level = "MEDIUM"
    elif score < 0.8:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return FraudInvestigationResponse(
        transaction=row,
        fraud_detected=row["is_fraud"],
        fraud_score=row["fraud_score"],
        risk_level=risk_level,
        triggered_rules=row["fraud_reasons"] or [],
    )