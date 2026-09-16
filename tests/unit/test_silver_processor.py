from datetime import datetime, timezone

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from fraud_detection.streaming.silver_processor import validate_transactions


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("TestSilverProcessor")
        .master("local[2]")
        .getOrCreate()
    )


def create_transaction_df(spark: SparkSession, **overrides):
    data = {
        "transaction_id": "TX-000001",
        "customer_id": "C-1001",
        "amount": 125.50,
        "currency": "EUR",
        "country": "ES",
        "merchant": "ONLINE_STORE",
        "timestamp": datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc),
        "device_id": "DEV-1001",
    }

    data.update(overrides)

    schema = StructType(
        [
            StructField("transaction_id", StringType(), True),
            StructField("customer_id", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("currency", StringType(), True),
            StructField("country", StringType(), True),
            StructField("merchant", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("device_id", StringType(), True),
        ]
    )

    return spark.createDataFrame([data], schema=schema)


def test_valid_transaction_passes():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark)

        result = validate_transactions(df)

        assert result.count() == 1
    finally:
        spark.stop()


def test_negative_amount_is_rejected():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark, amount=-10.0)

        result = validate_transactions(df)

        assert result.count() == 0
    finally:
        spark.stop()


def test_zero_amount_is_rejected():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark, amount=0.0)

        result = validate_transactions(df)

        assert result.count() == 0
    finally:
        spark.stop()


def test_invalid_currency_is_rejected():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark, currency="BTC")

        result = validate_transactions(df)

        assert result.count() == 0
    finally:
        spark.stop()


def test_missing_customer_id_is_rejected():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark, customer_id=None)

        result = validate_transactions(df)

        assert result.count() == 0
    finally:
        spark.stop()


def test_missing_device_id_is_rejected():
    spark = create_spark_session()

    try:
        df = create_transaction_df(spark, device_id=None)

        result = validate_transactions(df)

        assert result.count() == 0
    finally:
        spark.stop()