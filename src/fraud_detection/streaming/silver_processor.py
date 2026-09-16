from pyspark.sql import DataFrame
from pyspark.sql.functions import col

VALID_CURRENCIES = ["EUR", "USD", "GBP"]


def validate_transactions(df: DataFrame) -> DataFrame:
    return df.filter(
        col("transaction_id").isNotNull()
        & (col("transaction_id") != "")
        & col("customer_id").isNotNull()
        & (col("customer_id") != "")
        & col("amount").isNotNull()
        & (col("amount") > 0)
        & col("currency").isin(VALID_CURRENCIES)
        & col("country").isNotNull()
        & (col("country") != "")
        & col("merchant").isNotNull()
        & (col("merchant") != "")
        & col("timestamp").isNotNull()
        & col("device_id").isNotNull()
        & (col("device_id") != "")
    )