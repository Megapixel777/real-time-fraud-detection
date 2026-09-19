from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    array,
    col,
    lit,
    when,
)
from pyspark.sql.functions import (
    filter as spark_filter,
)

HIGH_AMOUNT_THRESHOLD = 5000.0


def build_fraud_signals(df: DataFrame) -> DataFrame:
    return (
        df.withColumn(
            "high_amount",
            col("amount") >= HIGH_AMOUNT_THRESHOLD,
        )
        .withColumn(
            "velocity_attack",
            col("transaction_count") >= 5,
        )
        .withColumn(
            "country_hopping",
            col("country_count") >= 3,
        )
        .withColumn(
            "multi_device",
            col("device_count") >= 3,
        )
    )


def build_fraud_decision(df: DataFrame) -> DataFrame:
    reasons = array(
        when(col("high_amount"), lit("HIGH_AMOUNT")),
        when(col("velocity_attack"), lit("VELOCITY_ATTACK")),
        when(col("country_hopping"), lit("COUNTRY_HOPPING")),
        when(col("multi_device"), lit("MULTI_DEVICE")),
    )

    return (
        df.withColumn(
            "fraud_score",
            (
                when(col("high_amount"), lit(0.30)).otherwise(lit(0.0))
                + when(col("velocity_attack"), lit(0.30)).otherwise(lit(0.0))
                + when(col("country_hopping"), lit(0.20)).otherwise(lit(0.0))
                + when(col("multi_device"), lit(0.20)).otherwise(lit(0.0))
            ),
        )
        .withColumn(
            "is_fraud",
            col("fraud_score") > 0,
        )
        .withColumn(
            "fraud_reasons",
            spark_filter(
                reasons,
                lambda reason: reason.isNotNull(),
            ),
        )
    )