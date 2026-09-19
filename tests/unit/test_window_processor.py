from datetime import datetime, timezone

from pyspark.sql import SparkSession

from fraud_detection.streaming.window_processor import (
    create_customer_windows,
    detect_velocity_attacks,
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("TestWindowProcessor")
        .master("local[2]")
        .getOrCreate()
    )


def test_create_customer_windows():
    spark = create_spark_session()

    try:
        data = [
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 0, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 20, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 40, tzinfo=timezone.utc),
            ),
        ]

        df = spark.createDataFrame(
            data,
            ["customer_id", "timestamp"],
        )

        result = create_customer_windows(df)

        rows = result.collect()

        assert len(rows) == 1
        assert rows[0]["customer_id"] == "C-1001"
        assert rows[0]["count"] == 3

    finally:
        spark.stop()


def test_detect_velocity_attacks():
    spark = create_spark_session()

    try:
        data = [
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 0, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 10, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 20, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 30, tzinfo=timezone.utc),
            ),
            (
                "C-1001",
                datetime(2026, 9, 18, 18, 0, 40, tzinfo=timezone.utc),
            ),
        ]

        df = spark.createDataFrame(
            data,
            ["customer_id", "timestamp"],
        )

        windowed_df = create_customer_windows(df)
        result = detect_velocity_attacks(windowed_df)

        rows = result.collect()

        assert len(rows) == 1
        assert rows[0]["customer_id"] == "C-1001"
        assert rows[0]["count"] == 5

    finally:
        spark.stop()

