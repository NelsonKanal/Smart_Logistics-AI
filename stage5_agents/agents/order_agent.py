from datetime import date, timedelta

from stage1_foundations.pricing import estimate_delivery
from stage3_systems.database import SessionLocal
from stage3_systems.models import Shipment


class OrderAgent:
    def run(self, customer, origin, destination, weight_kg, service):
        # Validate basic customer information.
        if not isinstance(customer, str) or not customer.strip():
            return {
                "success": False,
                "agent": "Order Agent",
                "message": "Customer name is required."
            }

        try:
            weight = float(weight_kg)

            quote = estimate_delivery(
                origin,
                destination,
                weight,
                service.strip().lower()
            )

        except (ValueError, TypeError, AttributeError) as error:
            return {
                "success": False,
                "agent": "Order Agent",
                "message": str(error)
            }

        today = date.today()
        days = 2 if quote["service"] == "express" else 5

        # Open a database session and save the shipment.
        with SessionLocal() as db:
            try:
                shipment_number = (
                    db.query(Shipment.id)
                    .order_by(Shipment.id.desc())
                    .first()
                )
                next_number = (
                    shipment_number[0] + 1 if shipment_number else 1
                )

                # Avoid using an ID that already exists.
                while True:
                    shipment_id = f"SL{next_number:05d}"
                    exists = (
                        db.query(Shipment.id)
                        .filter(
                            Shipment.shipment_id == shipment_id
                        )
                        .first()
                    )
                    if not exists:
                        break
                    next_number += 1

                shipment = Shipment(
                    shipment_id=shipment_id,
                    customer=customer.strip(),
                    origin=quote["origin"],
                    destination=quote["destination"],
                    weight_kg=weight,
                    service=quote["service"],
                    price_tzs=quote["price_tzs"],
                    status="Booked",
                    created_date=today,
                    expected_delivery=today + timedelta(days=days)
                )

                db.add(shipment)
                db.commit()
                db.refresh(shipment)

                return {
                    "success": True,
                    "agent": "Order Agent",
                    "shipment": {
                        "shipment_id": shipment.shipment_id,
                        "customer": shipment.customer,
                        "origin": shipment.origin,
                        "destination": shipment.destination,
                        "price_tzs": shipment.price_tzs,
                        "status": shipment.status,
                        "expected_delivery": (
                            shipment.expected_delivery.isoformat()
                        )
                    },
                    "message": (
                        f"Shipment {shipment.shipment_id} "
                        "was booked successfully."
                    )
                }

            except Exception:
                db.rollback()
                raise