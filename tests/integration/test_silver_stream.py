from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from fraud_detection.streaming.silver_processor import validate_transactions

TRANSACTION_SCHEMA = StructType(
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


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("TestSilverStream")
        .master("local[2]")
        .getOrCreate()
    )


def test_silver_processing_from_bronze(tmp_path: Path):
    spark = create_spark_session()

    try:
        transactions = [
            (
                "TX-000001",
                "C-1001",
                125.50,
                "EUR",
                "ES",
                "ONLINE_STORE",
                datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc),
                "DEV-1001",
            ),
            (
                "TX-000002",
                "C-1002",
                -50.00,
                "EUR",
                "ES",
                "ONLINE_STORE",
                datetime(2026, 9, 16, 20, 1, tzinfo=timezone.utc),
                "DEV-1002",
            ),
        ]

        bronze_path = tmp_path / "bronze"
        silver_path = tmp_path / "silver"

        bronze_df = spark.createDataFrame(
            transactions,
            schema=TRANSACTION_SCHEMA,
        )

        bronze_df.write.mode("overwrite").parquet(str(bronze_path))

        bronze_stream_df = (
            spark.readStream
            .schema(TRANSACTION_SCHEMA)
            .parquet(str(bronze_path))
        )

        silver_stream_df = validate_transactions(bronze_stream_df)

        query = (
            silver_stream_df
            .writeStream
            .format("parquet")
            .outputMode("append")
            .option("path", str(silver_path))
            .option(
                "checkpointLocation",
                str(tmp_path / "checkpoint"),
            )
            .trigger(availableNow=True)
            .start()
        )

        query.awaitTermination()

        result_df = spark.read.parquet(str(silver_path))

        assert result_df.count() == 1
        assert result_df.first()["transaction_id"] == "TX-000001"

    finally:
        spark.stop()