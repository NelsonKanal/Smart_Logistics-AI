
# main.py

from pricing import estimate_delivery


def main():
    print("=" * 40)
    print("   SMARTLOGISTICS AI")
    print("   Delivery Price Assistant")
    print("=" * 40)

    try:
        origin = input("Enter origin city: ")
        destination = input("Enter destination city: ")

        weight = float(input("Enter parcel weight (kg): "))

        service = input(
            "Choose service (standard/express): "
        ).strip().lower()

        if not service:
            service = "standard"

        quote = estimate_delivery(
            origin,
            destination,
            weight,
            service
        )

        print("\n--- DELIVERY QUOTATION ---")
        print(f"Origin: {quote['origin']}")
        print(f"Destination: {quote['destination']}")
        print(f"Weight: {quote['weight_kg']} kg")
        print(f"Service: {quote['service'].title()}")
        print(f"Route distance: {quote['distance_km']} km")
        print(f"Estimated price: TZS {quote['price_tzs']:,}")

        print("\nNote: This is a demonstration estimate,")
        print("not an official logistics company tariff.")

    except ValueError as error:
        print(f"\nUnable to calculate price: {error}")


if __name__ == "__main__":
    main()
