from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any


async def calculate_capacity_utilization_rate(
    total_vehicle_capacity: float,
    total_actual_load: float
) -> Dict[str, Any]:

    try:

        # Validate negative values
        if total_vehicle_capacity < 0 or total_actual_load < 0:
            raise ValueError("Negative capacity or load detected in database")

        # Prevent division by zero
        if total_vehicle_capacity == 0:
            return {
                "metric": "capacity_utilization_rate",
                "score": 0.0,
                "raw_data": {
                    "total_vehicle_capacity": total_vehicle_capacity,
                    "total_actual_load": total_actual_load,
                },
                "warning": "Total vehicle capacity is zero. Utilization set to 0.0",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        capacity_utilization_score = total_actual_load / total_vehicle_capacity
        capacity_utilization_score = float(capacity_utilization_score*100);

        return {
            "metric": "capacity_utilization_rate",
            "score": round(capacity_utilization_score, 2),
            "raw_data": {
                "total_vehicle_capacity": total_vehicle_capacity,
                "total_actual_load": total_actual_load,
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except ZeroDivisionError:
        return {
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": "Division by zero: total_vehicle_capacity is zero",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except ValueError as ve:
        return {
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": str(ve),
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except Exception as e:
        return {
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": f"Unexpected error: {str(e)}",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
