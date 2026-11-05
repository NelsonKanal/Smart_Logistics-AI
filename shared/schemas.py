from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ServiceType = Literal["standard", "express"]

ShipmentStatus = Literal[
    "Booked",
    "In Transit",
    "Delivered",
    "Cancelled",
]


class ShipmentRequest(BaseModel):
    customer: str = Field(min_length=1, max_length=100)
    origin: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    weight_kg: float = Field(gt=0)
    service: ServiceType = "standard"


class ShipmentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shipment_id: str
    customer: str
    origin: str
    destination: str
    weight_kg: float
    service: ServiceType
    price_tzs: int
    status: ShipmentStatus
    created_date: date
    expected_delivery: date


class AgentResponse(BaseModel):
    success: bool
    agent: str
    message: str