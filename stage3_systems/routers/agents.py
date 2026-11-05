from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from stage3_systems.auth import get_current_user
from stage3_systems.database import get_db
from stage3_systems.models import Shipment, User
from stage3_systems.schemas import AgentPriceRequest, AgentSupportRequest
from stage5_agents.coordinator import Coordinator

router = APIRouter(prefix="/agents", tags=["Stage 5 agents"])
coordinator = Coordinator()
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

@router.post("/price")
def run_pricing_agent(request: AgentPriceRequest, user: CurrentUser):
    # Fixed task name only; clients cannot select Python modules or commands.
    return coordinator.handle("price", {
        "origin": request.origin,
        "destination": request.destination,
        "weight_kg": str(request.weight_kg),
        "service": request.service,
    })
 
@router.get("/track/{shipment_id}")
def run_tracking_agent(shipment_id: str, user: CurrentUser, db: DbSession):
    query = db.query(Shipment).filter(Shipment.shipment_id == shipment_id)
    if user.role != "admin":
        query = query.filter(Shipment.owner_user_id == user.id)
    shipment = query.first()
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    # Ownership is checked before calling the existing tracking agent.
    return coordinator.handle("track", {"shipment_id": shipment_id})

@router.post("/support")
def run_support_agent(request: AgentSupportRequest, user: CurrentUser):
    return coordinator.handle("support", {"question": request.question})
