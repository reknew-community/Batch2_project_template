from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_ontime_pickup_rate(
    total_pickups: int,
    ontime_pickups: int
) -> Dict[str, Any]:
    try:

        if total_pickups == 0:
            return {
                "metric": "ontime_pickup",
                "score": 0.0,
                "raw_data": {
                    "total_pickups": 0,
                    "ontime_pickups": 0,
                    "ontime_percentage": 0.0
                },
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        ontime_percentage = (ontime_pickups / total_pickups) * 100.0
        score = round(ontime_percentage, 2)

        return {
            "metric": "ontime_pickup",
            "score": score,
            "raw_data": {
                "total_pickups": total_pickups,
                "ontime_pickups": ontime_pickups,
                "ontime_percentage": score
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except Exception as e:
        return {
            "metric": "ontime_pickup",
            "score": 0.0,
            "raw_data": None,
            "error": str(e),
            "error_type": type(e).__name__,
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
