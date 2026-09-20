from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


GOLD_PATH = "/opt/spark-apps/data/gold/fraud_transactions_stateful"

CHECKPOINT_PATH = (
    "/opt/spark-apps/data/gold/fraud_transactions_postgres_checkpoint"
)

POSTGRES_URL = "jdbc:postgresql://fraud-postgres:5432/fraud_detection"
POSTGRES_TABLE = "public.fraud_transactions"

POSTGRES_PROPERTIES = {
    "user": "fraud_user",
    "password": "fraud_password",
    "driver": "org.postgresql.Driver",
}


GOLD_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("timestamp", TimestampType(), False),
        StructField("amount", DoubleType(), False),
        StructField("currency", StringType(), False),
        StructField("country", StringType(), False),
        StructField("merchant", StringType(), False),
        StructField("device_id", StringType(), False),
        StructField("is_fraud", BooleanType(), False),
        StructField("fraud_score", DoubleType(), False),
        StructField(
            "fraud_reasons",
            ArrayType(StringType()),
            True,
        ),
    ]
)


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("GoldToPostgreSQL")
        .master("local[*]")
        .getOrCreate()
    )


def write_batch_to_postgres(
    batch_df: DataFrame,
    batch_id: int,
) -> None:
    if batch_df.isEmpty():
        return

    print(f"Writing batch {batch_id} to PostgreSQL")

    batch_df.select(
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
    ).write.jdbc(
        url=POSTGRES_URL,
        table=POSTGRES_TABLE,
        mode="append",
        properties=POSTGRES_PROPERTIES,
    )

    print(f"Batch {batch_id} written successfully")


def main() -> None:
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    gold_df = (
        spark.readStream
        .schema(GOLD_SCHEMA)
        .parquet(GOLD_PATH)
    )

    query = (
        gold_df.writeStream
        .foreachBatch(write_batch_to_postgres)
        .outputMode("append")
        .option(
            "checkpointLocation",
            CHECKPOINT_PATH,
        )
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()