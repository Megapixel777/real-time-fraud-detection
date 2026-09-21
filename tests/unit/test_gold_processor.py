from datetime import UTC, datetime

from pyspark.sql import SparkSession

from fraud_detection.streaming.gold_processor import (
    build_fraud_decision,
    build_fraud_signals,
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("TestGoldProcessor")
        .master("local[2]")
        .getOrCreate()
    )


def test_build_fraud_signals():
    spark = create_spark_session()

    try:
        data = [
            (
                "TX-000001",
                "C-1001",
                7500.0,
                "EUR",
                "ES",
                "ONLINE_STORE",
                datetime(
                    2026,
                    9,
                    18,
                    18,
                    0,
                    0,
                    tzinfo=UTC,
                ),
                "DEV-1001",
                5,
                3,
                3,
            ),
        ]

        df = spark.createDataFrame(
            data,
            [
                "transaction_id",
                "customer_id",
                "amount",
                "currency",
                "country",
                "merchant",
                "timestamp",
                "device_id",
                "transaction_count",
                "country_count",
                "device_count",
            ],
        )

        result = build_fraud_signals(df)

        row = result.collect()[0]

        assert row["transaction_id"] == "TX-000001"
        assert row["high_amount"] is True
        assert row["velocity_attack"] is True
        assert row["country_hopping"] is True
        assert row["multi_device"] is True

    finally:
        spark.stop()

def test_build_fraud_signals_for_normal_transaction():
    spark = create_spark_session()

    try:
        data = [
            (
                "TX-000002",
                "C-1002",
                100.0,
                "EUR",
                "ES",
                "SUPERMARKET",
                datetime(
                    2026,
                    9,
                    18,
                    18,
                    0,
                    0,
                    tzinfo=UTC,
                ),
                "DEV-2001",
                1,
                1,
                1,
            ),
        ]

        df = spark.createDataFrame(
            data,
            [
                "transaction_id",
                "customer_id",
                "amount",
                "currency",
                "country",
                "merchant",
                "timestamp",
                "device_id",
                "transaction_count",
                "country_count",
                "device_count",
            ],
        )

        result = build_fraud_signals(df)

        row = result.collect()[0]

        assert row["transaction_id"] == "TX-000002"
        assert row["high_amount"] is False
        assert row["velocity_attack"] is False
        assert row["country_hopping"] is False
        assert row["multi_device"] is False

    finally:
        spark.stop()

def test_build_fraud_decision():
    spark = create_spark_session()

    try:
        data = [
            (
                "TX-000003",
                "C-1001",
                7500.0,
                "EUR",
                "ES",
                "ONLINE_STORE",
                datetime(
                    2026,
                    9,
                    18,
                    18,
                    0,
                    0,
                    tzinfo=UTC,
                ),
                "DEV-1001",
                5,
                3,
                3,
            ),
        ]

        df = spark.createDataFrame(
            data,
            [
                "transaction_id",
                "customer_id",
                "amount",
                "currency",
                "country",
                "merchant",
                "timestamp",
                "device_id",
                "transaction_count",
                "country_count",
                "device_count",
            ],
        )

        signals_df = build_fraud_signals(df)
        result = build_fraud_decision(signals_df)

        row = result.collect()[0]

        assert row["is_fraud"] is True
        assert row["fraud_score"] == 1.0

        assert row["fraud_reasons"] == [
            "HIGH_AMOUNT",
            "VELOCITY_ATTACK",
            "COUNTRY_HOPPING",
            "MULTI_DEVICE",
        ]

    finally:
        spark.stop()