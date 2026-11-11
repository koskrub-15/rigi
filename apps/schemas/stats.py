from datetime import date
from pydantic import BaseModel, ConfigDict
from apps.core.tariffs import currency


class PerDaySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    day: date
    trips: int


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trips_count: int
    paid: int
    singles_price: int
    per_day: list[PerDaySchema]
    currency: str = currency
