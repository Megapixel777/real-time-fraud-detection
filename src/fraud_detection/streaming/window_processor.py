from pyspark.sql import DataFrame
from pyspark.sql.functions import col, collect_set, count, size, window


def create_customer_windows(
    df: DataFrame,
    window_seconds: int = 60,
) -> DataFrame:
    return df.groupBy(
        "customer_id",
        window("timestamp", f"{window_seconds} seconds"),
    ).count()


def detect_velocity_attacks(
    windowed_df: DataFrame,
    min_transactions: int = 5,
) -> DataFrame:
    return windowed_df.filter(
        col("count") >= min_transactions,
    )


def detect_country_hopping(
    df: DataFrame,
    min_countries: int = 3,
    window_seconds: int = 60,
) -> DataFrame:
    return (
        df.groupBy(
            "customer_id",
            window("timestamp", f"{window_seconds} seconds"),
        )
        .agg(
            size(
                collect_set("country"),
            ).alias("country_count"),
        )
        .filter(
            col("country_count") >= min_countries,
        )
    )


def detect_multi_device(
    df: DataFrame,
    min_devices: int = 3,
    window_seconds: int = 60,
) -> DataFrame:
    return (
        df.groupBy(
            "customer_id",
            window("timestamp", f"{window_seconds} seconds"),
        )
        .agg(
            size(
                collect_set("device_id"),
            ).alias("device_count"),
        )
        .filter(
            col("device_count") >= min_devices,
        )
    )

def create_fraud_windows(
    df: DataFrame,
    window_seconds: int = 60,
) -> DataFrame:
    return (
        df.groupBy(
            "customer_id",
            window("timestamp", f"{window_seconds} seconds"),
        )
        .agg(
            collect_set("country").alias("countries"),
            collect_set("device_id").alias("devices"),
            count("*").alias("transaction_count"),
        )
        .withColumn(
            "country_count",
            size(col("countries")),
        )
        .withColumn(
            "device_count",
            size(col("devices")),
        )
    )