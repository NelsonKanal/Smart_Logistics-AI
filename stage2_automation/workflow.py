
# workflow.py

import json
from pathlib import Path
from datetime import date, timedelta

from stage1_foundations.pricing import estimate_delivery
from stage2_automation.validation import validate_order


# Store the JSON file inside the Stage 2 folder.
DATA_FILE = Path(__file__).with_name("shipments.json")


def load_shipments():
    """Load saved shipments or return an empty list."""
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_shipments(shipments):
    """Save all shipment records to JSON."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(shipments, file, indent=4)


def create_shipment(order):
    """Validate, price, and save a new shipment."""

    # Step 1: Validate the order.
    errors = validate_order(order)

    if errors:
        return {
            "success": False,
            "errors": errors
        }

    try:
        # Step 2: Calculate the delivery estimate.
        quote = estimate_delivery(
            order["origin"],
            order["destination"],
            float(order["weight_kg"]),
            order["service"].strip().lower()
        )

    except (ValueError, TypeError) as error:
        return {
            "success": False,
            "errors": [str(error)]
        }

    # Step 3: Load existing shipments.
    shipments = load_shipments()

    # Step 4: Generate a unique ID based on existing IDs.
    existing_numbers = []

    for shipment in shipments:
        shipment_id = shipment.get("shipment_id", "")

        if shipment_id.startswith("SL"):
            try:
                existing_numbers.append(
                    int(shipment_id[2:])
                )
            except ValueError:
                pass

    next_number = max(existing_numbers, default=0) + 1
    shipment_id = f"SL{next_number:05d}"

    # Step 5: Calculate an illustrative delivery date.
    today = date.today()

    delivery_days = (
        2 if quote["service"] == "express" else 5
    )

    # Calendar days for this simple demonstration.
    expected_delivery = (
        today + timedelta(days=delivery_days)
    )

    # Step 6: Create the shipment record.
    shipment = {
        "shipment_id": shipment_id,
        "customer": order["customer"].strip(),
        "origin": quote["origin"],
        "destination": quote["destination"],
        "weight_kg": float(order["weight_kg"]),
        "service": quote["service"],
        "price_tzs": quote["price_tzs"],
        "status": "Booked",
        "created_date": today.isoformat(),
        "expected_delivery": expected_delivery.isoformat()
    }

    # Step 7: Save the record.
    shipments.append(shipment)
    save_shipments(shipments)

    return {
        "success": True,
        "shipment": shipment
    }


def find_overdue_shipments():
    """Find shipments past their expected delivery date."""
    shipments = load_shipments()
    today = date.today()
    overdue = []

    for shipment in shipments:
        if shipment["status"] in ("Delivered", "Cancelled"):
            continue

        expected = date.fromisoformat(
            shipment["expected_delivery"]
        )

        if expected < today:
            overdue.append(shipment)

    return overdue


def update_shipment_status(shipment_id, new_status):
    """Update the status of an existing shipment."""
    allowed_statuses = {
        "Booked",
        "In Transit",
        "Delivered",
        "Cancelled"
    }

    if new_status not in allowed_statuses:
        return {
            "success": False,
            "message": "Invalid shipment status."
        }

    shipments = load_shipments()

    for shipment in shipments:
        if shipment["shipment_id"] == shipment_id:
            shipment["status"] = new_status
            save_shipments(shipments)

            return {
                "success": True,
                "shipment": shipment
            }

    return {
        "success": False,
        "message": "Shipment not found."
    }
