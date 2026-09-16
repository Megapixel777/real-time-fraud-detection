from pyspark.sql import SparkSession

from fraud_detection.streaming.kafka_reader import TRANSACTION_SCHEMA
from fraud_detection.streaming.silver_processor import validate_transactions

BRONZE_PATH = "/opt/spark-apps/data/bronze/transactions"
SILVER_PATH = "/opt/spark-apps/data/silver/transactions"
CHECKPOINT_PATH = "/opt/spark-apps/data/silver/checkpoint"


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FraudDetectionSilver")
        .master("local[*]")
        .getOrCreate()
    )


def main() -> None:
    spark = create_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    bronze_df = (
        spark.readStream
        .schema(TRANSACTION_SCHEMA)
        .parquet(BRONZE_PATH)
    )

    silver_df = validate_transactions(bronze_df)

    query = (
        silver_df
        .writeStream
        .format("parquet")
        .outputMode("append")
        .option("path", SILVER_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()