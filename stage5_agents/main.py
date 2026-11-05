from stage3_systems.database import Base, engine
from stage3_systems import models

from stage5_agents.coordinator import Coordinator


def display_result(result):
    print(f"\nAgent: {result.get('agent', 'Unknown')}")
    print(result.get("message", ""))

    if "quote" in result:
        quote = result["quote"]
        print(f"Route: {quote['origin']} -> {quote['destination']}")
        print(f"Weight: {quote['weight_kg']} kg")
        print(f"Service: {quote['service']}")
        print(f"Distance: {quote['distance_km']} km")
        print(f"Price: TZS {quote['price_tzs']:,}")

    if "shipment" in result:
        for key, value in result["shipment"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    if "sources" in result:
        for number, source in enumerate(result["sources"], start=1):
            print(f"\nSource {number}: {source['source']}")
            print(f"Relevance: {source['score']}")
            print(source["text"])

    if not result.get("success", False):
        print("Task status: unsuccessful")


def main():
    # Create missing tables, without deleting existing records.
    Base.metadata.create_all(bind=engine)

    coordinator = Coordinator()

    while True:
        print("\n" + "=" * 45)
        print(" SMARTLOGISTICS AI - MULTI-AGENT SYSTEM")
        print("=" * 45)
        print("1. Calculate delivery price")
        print("2. Book a shipment")
        print("3. Track a shipment")
        print("4. Ask a company-policy question")
        print("5. Exit")

        choice = input("\nChoose an option: ").strip()

        try:
            if choice == "1":
                data = {
                    "origin": input("Origin city: ").strip(),
                    "destination": input("Destination city: ").strip(),
                    "weight_kg": input("Weight in kg: ").strip(),
                    "service": input(
                        "Service (standard/express): "
                    ).strip().lower()
                }
                result = coordinator.handle("price", data)

            elif choice == "2":
                data = {
                    "customer": input("Customer name: ").strip(),
                    "origin": input("Origin city: ").strip(),
                    "destination": input("Destination city: ").strip(),
                    "weight_kg": input("Weight in kg: ").strip(),
                    "service": input(
                        "Service (standard/express): "
                    ).strip().lower()
                }
                result = coordinator.handle("order", data)

            elif choice == "3":
                data = {
                    "shipment_id": input("Shipment ID: ").strip()
                }
                result = coordinator.handle("track", data)

            elif choice == "4":
                data = {
                    "question": input(
                        "Ask a question about company policies: "
                    ).strip()
                }
                result = coordinator.handle("support", data)

            elif choice == "5":
                print("SmartLogistics AI stopped.")
                break

            else:
                print("Invalid option. Please choose 1 to 5.")
                continue

            display_result(result)

        except (EOFError, KeyboardInterrupt):
            print("\nSmartLogistics AI stopped.")
            break


if __name__ == "__main__":
    main()