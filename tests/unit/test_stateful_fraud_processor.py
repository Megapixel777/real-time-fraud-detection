from datetime import UTC, datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from fraud_detection.streaming.stateful_fraud_processor import (
    build_stateful_fraud_windows,
    flatten_stateful_fraud_windows,
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("TestStatefulFraudProcessor")
        .master("local[2]")
        .getOrCreate()
    )


def test_build_stateful_fraud_windows():
    spark = create_spark_session()

    try:
        data = [
            (
                "TX-000001",
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 0, tzinfo=UTC),
                100.0,
                "EUR",
                "ES",
                "ONLINE_STORE",
                "DEV-1001",
            ),
            (
                "TX-000002",
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 10, tzinfo=UTC),
                200.0,
                "EUR",
                "FR",
                "ONLINE_STORE",
                "DEV-2001",
            ),
            (
                "TX-000003",
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 20, tzinfo=UTC),
                300.0,
                "EUR",
                "DE",
                "ONLINE_STORE",
                "DEV-3001",
            ),
            (
                "TX-000004",
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 30, tzinfo=UTC),
                150.0,
                "EUR",
                "ES",
                "ONLINE_STORE",
                "DEV-1001",
            ),
            (
                "TX-000005",
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 40, tzinfo=UTC),
                250.0,
                "EUR",
                "FR",
                "ONLINE_STORE",
                "DEV-2001",
            ),
        ]

        df = spark.createDataFrame(
            data,
            [
                "transaction_id",
                "customer_id",
                "timestamp",
                "amount",
                "currency",
                "country",
                "merchant",
                "device_id",
            ],
        )

        result = build_stateful_fraud_windows(df)

        rows = result.collect()

        assert len(rows) == 1

        row = rows[0]

        assert row["customer_id"] == "C-1001"
        assert row["transaction_count"] == 5
        assert len(row["countries"]) == 3
        assert len(row["devices"]) == 3
        assert len(row["transactions"]) == 5

    finally:
        spark.stop()


def test_flatten_stateful_fraud_windows():
    spark = create_spark_session()

    try:
        data = [
            (
                "TX-001",
                "C-1001",
                100.0,
                "EUR",
                "ES",
                "SHOP",
                "2026-09-18 12:00:00",
                "DEV-001",
            ),
            (
                "TX-002",
                "C-1001",
                200.0,
                "EUR",
                "FR",
                "SHOP",
                "2026-09-18 12:00:05",
                "DEV-002",
            ),
            (
                "TX-003",
                "C-1001",
                300.0,
                "EUR",
                "DE",
                "SHOP",
                "2026-09-18 12:00:10",
                "DEV-003",
            ),
            (
                "TX-004",
                "C-1001",
                400.0,
                "EUR",
                "ES",
                "SHOP",
                "2026-09-18 12:00:15",
                "DEV-001",
            ),
            (
                "TX-005",
                "C-1001",
                500.0,
                "EUR",
                "FR",
                "SHOP",
                "2026-09-18 12:00:20",
                "DEV-002",
            ),
        ]

        columns = [
            "transaction_id",
            "customer_id",
            "amount",
            "currency",
            "country",
            "merchant",
            "timestamp",
            "device_id",
        ]

        df = spark.createDataFrame(
            data,
            columns,
        ).withColumn(
            "timestamp",
            col("timestamp").cast("timestamp"),
        )

        windowed_df = build_stateful_fraud_windows(df)

        result = flatten_stateful_fraud_windows(windowed_df)

        rows = result.collect()

        assert len(rows) == 5
        assert all(row["transaction_count"] == 5 for row in rows)
        assert all(row["country_count"] == 3 for row in rows)
        assert all(row["device_count"] == 3 for row in rows)

    finally:
        spark.stop()