
# main.py

from stage2_automation.workflow import (
    create_shipment,
    load_shipments,
    find_overdue_shipments,
    update_shipment_status
)


def create_order_menu():
    print("\n--- NEW DELIVERY ORDER ---")

    order = {
        "customer": input("Customer name: "),
        "origin": input("Origin city: "),
        "destination": input("Destination city: "),
        "weight_kg": input("Parcel weight (kg): "),
        "service": input(
            "Service (standard/express): "
        ).strip().lower()
    }

    result = create_shipment(order)

    if result["success"]:
        shipment = result["shipment"]

        print("\nShipment created successfully!")
        print(f"Shipment ID: {shipment['shipment_id']}")
        print(f"Customer: {shipment['customer']}")
        print(
            f"Estimated price: TZS "
            f"{shipment['price_tzs']:,}"
        )
        print(
            f"Expected delivery: "
            f"{shipment['expected_delivery']}"
        )
        print("Status: Booked")

    else:
        print("\nOrder could not be created.")

        for error in result["errors"]:
            print(f"- {error}")


def view_shipments_menu():
    shipments = load_shipments()

    if not shipments:
        print("\nNo shipments have been saved yet.")
        return

    print("\n--- ALL SHIPMENTS ---")

    for shipment in shipments:
        print("-" * 35)
        print(f"ID: {shipment['shipment_id']}")
        print(f"Customer: {shipment['customer']}")
        print(
            f"Route: {shipment['origin']} -> "
            f"{shipment['destination']}"
        )
        print(f"Price: TZS {shipment['price_tzs']:,}")
        print(f"Status: {shipment['status']}")


def update_status_menu():
    shipment_id = input("Enter shipment ID: ").strip()

    print("Available statuses:")
    print("1. Booked")
    print("2. In Transit")
    print("3. Delivered")
    print("4. Cancelled")

    choices = {
        "1": "Booked",
        "2": "In Transit",
        "3": "Delivered",
        "4": "Cancelled"
    }

    choice = input("Choose status: ").strip()

    if choice not in choices:
        print("Invalid status choice.")
        return

    result = update_shipment_status(
        shipment_id,
        choices[choice]
    )

    if result["success"]:
        print("Shipment status updated successfully.")
    else:
        print(result["message"])


def overdue_menu():
    overdue = find_overdue_shipments()

    print("\n--- OVERDUE SHIPMENTS ---")

    if not overdue:
        print("No overdue shipments found.")
        return

    for shipment in overdue:
        print(
            f"{shipment['shipment_id']} | "
            f"{shipment['customer']} | "
            f"Expected: {shipment['expected_delivery']}"
        )


def main():
    while True:
        print("\n==============================")
        print(" SMARTLOGISTICS AUTOMATION")
        print("==============================")
        print("1. Create delivery order")
        print("2. View all shipments")
        print("3. Update shipment status")
        print("4. Check overdue shipments")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_order_menu()

        elif choice == "2":
            view_shipments_menu()

        elif choice == "3":
            update_status_menu()

        elif choice == "4":
            overdue_menu()

        elif choice == "5":
            print("SmartLogistics stopped.")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
