from datetime import date, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from stage1_foundations.pricing import estimate_delivery
from stage3_systems.auth import get_current_user, require_admin
from stage3_systems.database import get_db
from stage3_systems.models import Shipment, User
from stage3_systems.schemas import ShipmentCreate, ShipmentResponse, StatusUpdate, QuoteRequest

router = APIRouter(prefix="/shipments", tags=["Shipments"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]

def generate_shipment_id(db: Session) -> str:
    latest = db.query(Shipment).order_by(Shipment.id.desc()).first()
    next_number = latest.id + 1 if latest else 1
    while True:
        candidate = f"SL{next_number:05d}"
        if not db.query(Shipment).filter(Shipment.shipment_id == candidate).first():
            return candidate
        next_number += 1

@router.post("/quote")
def get_delivery_quote(order: QuoteRequest, user: CurrentUser):
    try:
        quote = estimate_delivery(order.origin, order.destination, order.weight_kg, order.service)
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"success": True, "quote": quote, "message": "Price estimate calculated successfully."}

@router.post("/", response_model=ShipmentResponse, status_code=201)
def create_shipment(order: ShipmentCreate, user: CurrentUser, db: DbSession):
    try:
        quote = estimate_delivery(order.origin, order.destination, order.weight_kg, order.service)
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    today = date.today()
    shipment = Shipment(
        shipment_id=generate_shipment_id(db),
        owner_user_id=user.id,
        customer=user.full_name,
        origin=quote["origin"],
        destination=quote["destination"],
        weight_kg=order.weight_kg,
        service=quote["service"],
        price_tzs=quote["price_tzs"],
        status="Booked",
        created_date=today,
        expected_delivery=today + timedelta(days=2 if quote["service"] == "express" else 5),
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

@router.get("/", response_model=list[ShipmentResponse])
def get_shipments(user: CurrentUser, db: DbSession):
    query = db.query(Shipment)
    if user.role != "admin":
        query = query.filter(Shipment.owner_user_id == user.id)
    return query.order_by(Shipment.id.desc()).all()

@router.get("/overdue", response_model=list[ShipmentResponse])
def get_overdue_shipments(user: CurrentUser, db: DbSession):
    query = db.query(Shipment).filter(
        Shipment.expected_delivery < date.today(),
        Shipment.status.notin_(["Delivered", "Cancelled"]),
    )
    if user.role != "admin":
        query = query.filter(Shipment.owner_user_id == user.id)
    return query.order_by(Shipment.expected_delivery.asc()).all()

@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: str, user: CurrentUser, db: DbSession):
    query = db.query(Shipment).filter(Shipment.shipment_id == shipment_id)
    if user.role != "admin":
        query = query.filter(Shipment.owner_user_id == user.id)
    shipment = query.first()
    if shipment is None:
        # Do not reveal whether another customer's shipment exists.
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment

@router.patch("/{shipment_id}/status", response_model=ShipmentResponse)
def update_shipment_status(shipment_id: str, update: StatusUpdate, user: AdminUser, db: DbSession):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    shipment.status = update.status
    db.commit()
    db.refresh(shipment)
    return shipment
