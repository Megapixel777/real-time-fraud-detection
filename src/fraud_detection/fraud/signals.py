from pydantic import BaseModel


class FraudSignals(BaseModel):
    high_amount: bool
    velocity_attack: bool
    country_hopping: bool
    multi_device: bool