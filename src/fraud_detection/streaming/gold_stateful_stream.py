from pyspark.sql import SparkSession

from fraud_detection.streaming.gold_processor import (
    build_fraud_decision,
    build_fraud_signals,
)
from fraud_detection.streaming.kafka_reader import TRANSACTION_SCHEMA
from fraud_detection.streaming.stateful_fraud_processor import (
    build_stateful_fraud_windows,
    flatten_stateful_fraud_windows,
)


SILVER_PATH = "/opt/spark-apps/data/silver/transactions"
GOLD_PATH = "/opt/spark-apps/data/gold/fraud_transactions_stateful"
CHECKPOINT_PATH = (
    "/opt/spark-apps/data/gold/fraud_transactions_stateful_checkpoint"
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FraudDetectionStatefulGold")
        .master("local[*]")
        .getOrCreate()
    )


def main() -> None:
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    silver_df = (
        spark.readStream
        .schema(TRANSACTION_SCHEMA)
        .parquet(SILVER_PATH)
    )

    windowed_df = build_stateful_fraud_windows(
        silver_df,
        window_seconds=60,
        watermark_seconds=10,
    )

    transactions_df = flatten_stateful_fraud_windows(
        windowed_df,
    )

    signals_df = build_fraud_signals(
        transactions_df,
    )

    result_df = build_fraud_decision(
        signals_df,
    )

    gold_df = result_df.select(
        "transaction_id",
        "customer_id",
        "timestamp",
        "amount",
        "currency",
        "country",
        "merchant",
        "device_id",
        "is_fraud",
        "fraud_score",
        "fraud_reasons",
    )

    query = (
        gold_df.writeStream
        .format("parquet")
        .outputMode("append")
        .option("path", GOLD_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()