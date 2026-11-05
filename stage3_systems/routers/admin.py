from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from stage3_systems.auth import require_admin
from stage3_systems.database import get_db
from stage3_systems.models import Shipment, User
 
router = APIRouter(prefix="/admin", tags=["Administration"])
AdminUser = Annotated[User, Depends(require_admin)]
DbSession = Annotated[Session, Depends(get_db)]

@router.get("/unassigned-shipments")
def list_unassigned_shipments(admin: AdminUser, db: DbSession):
    # Existing shipments remain hidden from customer accounts until explicitly assigned.
    rows = db.query(Shipment).filter(Shipment.owner_user_id.is_(None)).order_by(Shipment.id.desc()).all()
    return [{
        "shipment_id": s.shipment_id, "customer": s.customer, "origin": s.origin,
        "destination": s.destination, "status": s.status
    } for s in rows]

@router.post("/shipments/{shipment_id}/assign/{user_id}")
def assign_legacy_shipment(shipment_id: str, user_id: int, admin: AdminUser, db: DbSession):
    shipment = db.query(Shipment).filter(
        Shipment.shipment_id == shipment_id, Shipment.owner_user_id.is_(None)
    ).first()
    user = db.query(User).filter(User.id == user_id).first()
    if shipment is None or user is None:
        raise HTTPException(status_code=404, detail="Unassigned shipment or user not found.")
    shipment.owner_user_id = user.id
    # Do not silently overwrite the original customer label; an admin should verify
    # the recipient before assigning the record.
    db.commit()
    return {"success": True, "shipment_id": shipment.shipment_id, "assigned_user_id": user.id}
