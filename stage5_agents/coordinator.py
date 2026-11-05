from stage5_agents.agents.order_agent import OrderAgent
from stage5_agents.agents.pricing_agent import PricingAgent
from stage5_agents.agents.tracking_agent import TrackingAgent
from stage5_agents.agents.support_agent import SupportAgent


class Coordinator:
    def __init__(self):
        self.order_agent = OrderAgent()
        self.pricing_agent = PricingAgent()
        self.tracking_agent = TrackingAgent()
        self.support_agent = SupportAgent()

    def handle(self, task, data):
        """Route a task to the appropriate specialist."""
        try:
            if task == "price":
                return self.pricing_agent.run(
                    origin=data["origin"],
                    destination=data["destination"],
                    weight_kg=data["weight_kg"],
                    service=data["service"]
                )

            if task == "order":
                return self.order_agent.run(
                    customer=data["customer"],
                    origin=data["origin"],
                    destination=data["destination"],
                    weight_kg=data["weight_kg"],
                    service=data["service"]
                )

            if task == "track":
                return self.tracking_agent.run(
                    shipment_id=data["shipment_id"]
                )

            if task == "support":
                return self.support_agent.run(
                    question=data["question"]
                )

            return {
                "success": False,
                "agent": "Coordinator",
                "message": "Unknown task. Please select a valid option."
            }

        except Exception:
            # Avoid exposing internal errors to the user.
            # Investigate the terminal logs while developing.
            return {
                "success": False,
                "agent": "Coordinator",
                "message": (
                    "The task could not be completed. "
                    "Check the application and database configuration."
                )
            }