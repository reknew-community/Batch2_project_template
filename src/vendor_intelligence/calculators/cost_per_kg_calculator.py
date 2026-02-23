from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any


async def calculate_cost_competitiveness(
    total_cost_vendor: float,
    weight_kg_vendor: float,
    total_cost_market: float,
    weight_kg_market: float
) -> Dict[str, Any]:
    

    print(total_cost_vendor);
    print(weight_kg_vendor);
    print(total_cost_market);
    print(weight_kg_market);

    try:

        # Vendor has no shipments
        if weight_kg_vendor == 0:
            return {
                "metric": "cost_per_kg",
                "score": 0.0,
                "raw_data": None,
                "warning": "Vendor has no shipment weight in selected period",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        # Market has no shipments
        if weight_kg_market == 0:
            return {
                "metric": "cost_per_kg",
                "score": 50.0,
                "raw_data": None,
                "warning": "Market shipment weight is zero; default neutral score applied",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        # Calculate rates
        cost_per_kg = total_cost_vendor / weight_kg_vendor
        market_rate_per_kg = total_cost_market / weight_kg_market

        # Round to 4 decimal places
        cost_per_kg = round(cost_per_kg, 4)
        market_rate_per_kg = round(market_rate_per_kg, 4)

        # Extra protection
        if market_rate_per_kg == 0:
            score = 50.0
        else:
            cost_ratio = cost_per_kg / market_rate_per_kg

            if cost_ratio <= 0.8:
                score = 100.0
            elif cost_ratio <= 1.0:
                score = 75.0 + (1.0 - cost_ratio) * 125.0
            elif cost_ratio <= 1.5:
                score = 75.0 - (cost_ratio - 1.0) * 120.0
            else:
                score = 0.0

        # Clamp score between 0 and 100
        score = max(0.0, min(100.0, score))

        # Round to 2 decimal places
        score = round(score, 2)

        return {
            "metric": "cost_per_kg",
            "score": score,
            "raw_data": {
                "vendor": {
                    "total_cost": total_cost_vendor,
                    "weight_kg": weight_kg_vendor,
                    "cost_per_kg": cost_per_kg
                },
                "market": {
                    "total_cost": total_cost_market,
                    "weight_kg": weight_kg_market,
                    "market_rate_per_kg": market_rate_per_kg
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except ZeroDivisionError:
        return {
            "metric": "cost_per_kg",
            "score": 0.0,
            "raw_data": None,
            "error": "Division by zero encountered during cost calculation",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except Exception as e:
        return {
            "metric": "cost_per_kg",
            "score": 0.0,
            "raw_data": None,
            "error": f"Unexpected error: {str(e)}",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }