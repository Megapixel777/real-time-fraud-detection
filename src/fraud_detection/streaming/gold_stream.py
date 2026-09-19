from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from fraud_detection.streaming.gold_processor import (
    build_fraud_decision,
    build_fraud_signals,
)
from fraud_detection.streaming.kafka_reader import TRANSACTION_SCHEMA
from fraud_detection.streaming.window_processor import create_fraud_windows

SILVER_PATH = "/opt/spark-apps/data/silver/transactions"

GOLD_PATH = "/opt/spark-apps/data/gold/fraud_transactions"
CHECKPOINT_PATH = "/opt/spark-apps/data/gold/fraud_transactions_checkpoint"


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FraudDetectionGold")
        .master("local[*]")
        .getOrCreate()
    )


def process_batch(batch_df: DataFrame, batch_id: int) -> None:
    if batch_df.isEmpty():
        return

    windows_df = create_fraud_windows(batch_df)

    enriched_df = (
    batch_df.alias("tx")
    .join(
        windows_df.alias("win"),
        (
            (col("tx.customer_id") == col("win.customer_id"))
            & (col("tx.timestamp") >= col("win.window.start"))
            & (col("tx.timestamp") < col("win.window.end"))
        ),
        how="left",
    )
    .select(
        col("tx.*"),
        col("win.transaction_count"),
        col("win.country_count"),
        col("win.device_count"),
    )
)

    signals_df = build_fraud_signals(enriched_df)

    result_df = build_fraud_decision(signals_df)

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

    gold_df.write.mode("append").parquet(GOLD_PATH)

    print(
        f"[Gold] batch_id={batch_id} | "
        f"rows={gold_df.count()}"
    )


def main() -> None:
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    silver_df = (
        spark.readStream
        .schema(TRANSACTION_SCHEMA)
        .parquet(SILVER_PATH)
    )

    query = (
        silver_df.writeStream
        .foreachBatch(process_batch)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()