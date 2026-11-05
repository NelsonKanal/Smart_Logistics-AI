from datetime import date
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from stage3_systems.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    is_active = Column(Integer, nullable=False, default=1)
    shipments = relationship("Shipment", back_populates="owner")

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String(20), unique=True, index=True, nullable=False)
    # Nullable only to preserve legacy rows during migration. Legacy rows are not
    # visible to customers until an admin assigns them.
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User", back_populates="shipments")
    customer = Column(String(100), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    weight_kg = Column(Float, nullable=False)
    service = Column(String(20), nullable=False)
    price_tzs = Column(Integer, nullable=False)
    status = Column(String(30), default="Booked", nullable=False)
    created_date = Column(Date, default=date.today, nullable=False)
    expected_delivery = Column(Date, nullable=False)
