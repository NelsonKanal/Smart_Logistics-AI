
# validation.py

ALLOWED_SERVICES = {"standard", "express"}


def validate_order(order):
    """Return a list of errors found in a delivery order."""
    errors = []

    required_fields = [
        "customer",
        "origin",
        "destination",
        "weight_kg",
        "service",
    ]

    # Check required fields.
    for field in required_fields:
        value = order.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            errors.append(f"{field} is required.")

    # Check parcel weight.
    if order.get("weight_kg") is not None:
        try:
            weight = float(order["weight_kg"])

            if weight <= 0:
                errors.append(
                    "Parcel weight must be greater than zero."
                )

        except (ValueError, TypeError):
            errors.append("Parcel weight must be a number.")

    # Check delivery service.
    service = order.get("service")

    if isinstance(service, str):
        service = service.strip().lower()

    if service not in ALLOWED_SERVICES:
        errors.append(
            "Service must be standard or express."
        )

    return errors
