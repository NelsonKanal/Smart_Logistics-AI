
# pricing.py

# Demonstration route distances in kilometres.
# These are sample values, not live route measurements.
ROUTES_KM = {
    ("Dodoma", "Dar es Salaam"): 450,
    ("Dodoma", "Arusha"): 400,
    ("Dar es Salaam", "Arusha"): 640,
}



def normalize_city(city):
    """Return a consistent spelling for supported cities."""
    cleaned = " ".join(city.strip().split()).casefold()

    cities = {
        "dodoma": "Dodoma",
        "dar es salaam": "Dar es Salaam",
        "arusha": "Arusha",
    }

    if cleaned not in cities:
        raise ValueError(f"Unsupported city: {city}")

    return cities[cleaned]


def get_distance(origin, destination):
    """Find the distance for a supported route."""
    origin = normalize_city(origin)
    destination = normalize_city(destination)

    if origin == destination:
        return 20

    # Check the route in either direction.
    distance = ROUTES_KM.get((origin, destination))

    if distance is None:
        distance = ROUTES_KM.get((destination, origin))

    if distance is None:
        raise ValueError(
            f"Unsupported route: {origin} to {destination}"
        )

    return distance


def estimate_delivery(origin, destination, weight_kg, service="standard"):
    """Calculate an illustrative delivery price."""

    if weight_kg <= 0:
        raise ValueError("Parcel weight must be greater than zero.")

    service = service.strip().lower()

    if service not in ("standard", "express"):
        raise ValueError("Service must be standard or express.")

    origin = normalize_city(origin)
    destination = normalize_city(destination)

    distance = get_distance(origin, destination)

    # Demonstration pricing rules, not official company rates.
    base_fee = 2500
    weight_fee = weight_kg * 800
    distance_fee = distance * 5

    subtotal = base_fee + weight_fee + distance_fee

    # Express service costs 40% more in this example.
    if service == "express":
        subtotal *= 1.40

    return {
        "origin": origin,
        "destination": destination,
        "weight_kg": weight_kg,
        "service": service,
        "distance_km": distance,
        "price_tzs": round(subtotal),
    }
