from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
KAFKA_TOPIC = "fraud-transactions"

BRONZE_PATH = "/opt/spark-apps/data/bronze/transactions"
CHECKPOINT_PATH = "/opt/spark-apps/data/bronze/checkpoint"


TRANSACTION_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("amount", DoubleType(), False),
        StructField("currency", StringType(), False),
        StructField("country", StringType(), False),
        StructField("merchant", StringType(), False),
        StructField("timestamp", TimestampType(), False),
        StructField("device_id", StringType(), False),
    ]
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FraudDetectionKafkaReader")
        .master("local[*]")
        .getOrCreate()
    )


def main() -> None:
    spark = create_spark_session()

    spark.sparkContext.setLogLevel("WARN")

    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    transactions_df = (
        kafka_df
        .select(
            from_json(
                col("value").cast("string"),
                TRANSACTION_SCHEMA,
            ).alias("transaction")
        )
        .select("transaction.*")
    )

    query = (
        transactions_df
        .writeStream
        .format("parquet")
        .outputMode("append")
        .option("path", BRONZE_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()