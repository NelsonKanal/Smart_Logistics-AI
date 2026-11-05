from stage1_foundations.pricing import estimate_delivery


class PricingAgent:
    def run(self, origin, destination, weight_kg, service="standard"):
        try:
            quote = estimate_delivery(
                origin=origin,
                destination=destination,
                weight_kg=float(weight_kg),
                service=service.strip().lower()
            )

            return {
                "success": True,
                "agent": "Pricing Agent",
                "quote": quote,
                "message": (
                    f"Estimated delivery cost: "
                    f"TZS {quote['price_tzs']:,}"
                )
            }

        except (ValueError, TypeError, AttributeError) as error:
            return {
                "success": False,
                "agent": "Pricing Agent",
                "message": str(error)
            }