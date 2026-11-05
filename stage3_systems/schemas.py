from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ShipmentCreate(BaseModel):
    origin: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    weight_kg: float = Field(gt=0, le=10000)
    service: Literal["standard", "express"] = "standard"

class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    shipment_id: str
    customer: str
    origin: str
    destination: str
    weight_kg: float
    service: str
    price_tzs: int
    status: str
    created_date: date
    expected_delivery: date

class StatusUpdate(BaseModel):
    status: Literal["Booked", "In Transit", "Delivered", "Cancelled"]

class QuoteRequest(BaseModel):
    origin: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    weight_kg: float = Field(gt=0, le=10000)
    service: Literal["standard", "express"] = "standard"

class AgentPriceRequest(QuoteRequest):
    pass

class AgentSupportRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
