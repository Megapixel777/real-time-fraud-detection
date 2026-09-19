from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window

from fraud_detection.streaming.kafka_reader import TRANSACTION_SCHEMA

SILVER_PATH = "/opt/spark-apps/data/silver/transactions"
VELOCITY_PATH = "/opt/spark-apps/data/gold/velocity_attacks"
CHECKPOINT_PATH = "/opt/spark-apps/data/gold/velocity_checkpoint"


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FraudDetectionVelocity")
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

    velocity_df = (
        silver_df
        .withWatermark("timestamp", "10 seconds")
        .groupBy(
            "customer_id",
            window("timestamp", "60 seconds"),
        )
        .count()
        .filter(col("count") >= 5)
    )

    query = (
        velocity_df
        .writeStream
        .format("parquet")
        .outputMode("append")
        .option("path", VELOCITY_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()