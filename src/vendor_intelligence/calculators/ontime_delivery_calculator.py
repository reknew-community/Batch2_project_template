from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime
from typing import Dict, Any

from vendor_intelligence.models.trip import Trip

async def calculate_ontime_delivery_rate(
    total_deliveries: int,
    ontime_deliveries: int
) -> Dict[str, Any]:

    try:

        if total_deliveries == 0:
            return {
                "metric": "ontime_delivery",
                "score": 0.0,
                "raw_data": {
                    "total_deliveries": 0,
                    "ontime_deliveries": 0,
                    "ontime_percentage": 0.0
                },
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        ontime_percentage = (ontime_deliveries / total_deliveries) * 100.0
        score = round(ontime_percentage, 2)

        return {
            "metric": "ontime_delivery",
            "score": score,
            "raw_data": {
                "total_deliveries": total_deliveries,
                "ontime_deliveries": ontime_deliveries,
                "ontime_percentage": score
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except Exception as e:
        return {
            "metric": "ontime_delivery",
            "score": 0.0,
            "raw_data": None,
            "error": str(e),
            "error_type": type(e).__name__,
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
