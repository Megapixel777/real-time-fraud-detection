from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    collect_list,
    collect_set,
    count,
    explode,
    size,
    struct,
    window,
)


def build_stateful_fraud_windows(
    df: DataFrame,
    window_seconds: int = 60,
    watermark_seconds: int = 10,
) -> DataFrame:
    return (
        df.withWatermark(
            "timestamp",
            f"{watermark_seconds} seconds",
        )
        .groupBy(
            "customer_id",
            window("timestamp", f"{window_seconds} seconds"),
        )
        .agg(
            collect_list(
                struct(
                    "transaction_id",
                    "timestamp",
                    "amount",
                    "currency",
                    "country",
                    "merchant",
                    "device_id",
                )
            ).alias("transactions"),
            collect_set("country").alias("countries"),
            collect_set("device_id").alias("devices"),
            count("*").alias("transaction_count"),
        )
    )


def flatten_stateful_fraud_windows(
    windowed_df: DataFrame,
) -> DataFrame:
    return (
        windowed_df
        .withColumn(
            "country_count",
            size(col("countries")),
        )
        .withColumn(
            "device_count",
            size(col("devices")),
        )
        .withColumn(
            "transaction",
            explode(col("transactions")),
        )
        .select(
            "customer_id",
            "window",
            col("transaction.transaction_id").alias("transaction_id"),
            col("transaction.timestamp").alias("timestamp"),
            col("transaction.amount").alias("amount"),
            col("transaction.currency").alias("currency"),
            col("transaction.country").alias("country"),
            col("transaction.merchant").alias("merchant"),
            col("transaction.device_id").alias("device_id"),
            "transaction_count",
            "country_count",
            "device_count",
        )
    )