from pyspark.sql import DataFrame
from pyspark.sql.functions import col, window


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