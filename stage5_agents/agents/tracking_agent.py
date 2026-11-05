from datetime import date

from stage3_systems.database import SessionLocal
from stage3_systems.models import Shipment


class TrackingAgent:
    def run(self, shipment_id):
        if not shipment_id or not shipment_id.strip():
            return {
                "success": False,
                "agent": "Tracking Agent",
                "message": "Please provide a shipment ID."
            }

        with SessionLocal() as db:
            shipment = (
                db.query(Shipment)
                .filter(
                    Shipment.shipment_id == shipment_id.strip().upper()
                )
                .first()
            )

            if shipment is None:
                return {
                    "success": False,
                    "agent": "Tracking Agent",
                    "message": "Shipment not found."
                }

            is_overdue = (
                shipment.expected_delivery < date.today()
                and shipment.status not in {"Delivered", "Cancelled"}
            )

            return {
                "success": True,
                "agent": "Tracking Agent",
                "shipment": {
                    "shipment_id": shipment.shipment_id,
                    "customer": shipment.customer,
                    "origin": shipment.origin,
                    "destination": shipment.destination,
                    "status": shipment.status,
                    "expected_delivery": (
                        shipment.expected_delivery.isoformat()
                    ),
                    "overdue": is_overdue
                },
                "message": (
                    "Shipment information retrieved from the database."
                )
            }