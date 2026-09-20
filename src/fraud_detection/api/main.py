from fastapi import FastAPI, HTTPException, Query

from fraud_detection.api.database import get_connection
from fraud_detection.api.models import TransactionResponse


app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for querying fraud detection transactions.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return {"status": "healthy", "database": "connected"}

    except Exception:
        return {"status": "unhealthy", "database": "unavailable"}


@app.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
def get_transactions(
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
        ORDER BY timestamp DESC
        LIMIT %s
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (limit,))
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

    with get_connection() as connection:
        with connection.cursor() as cursor:
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

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

    return rows