from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any


async def calculate_capacity_utilization_rate(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:

    try:
        query = text("""
            SELECT 
                COALESCE(SUM(t.vehicle_capacity_kg), 0) AS total_vehicle_capacity,
                COALESCE(SUM(t.actual_load_kg), 0) AS total_actual_load
            FROM trips t
            WHERE t.vendor_id = :vendor_id
            AND t.scheduled_departure BETWEEN :start_date AND :end_date
            AND t.status IN ('COMPLETED','IN_TRANSIT')
            AND t.actual_departure IS NOT NULL
            AND t.scheduled_departure IS NOT NULL
        """)

        result = db.execute(
            query,
            {
                "vendor_id": vendor_id,
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()

        if result is None:
            raise ValueError("No data returned from database")

        total_vehicle_capacity = result.total_vehicle_capacity or 0
        total_actual_load = result.total_actual_load or 0

        # Validate negative values
        if total_vehicle_capacity < 0 or total_actual_load < 0:
            raise ValueError("Negative capacity or load detected in database")

        # Prevent division by zero
        if total_vehicle_capacity == 0:
            return {
                "vendor_id": vendor_id,
                "metric": "capacity_utilization_rate",
                "score": 0.0,
                "raw_data": {
                    "total_vehicle_capacity": total_vehicle_capacity,
                    "total_actual_load": total_actual_load,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                },
                "warning": "Total vehicle capacity is zero. Utilization set to 0.0",
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        capacity_utilization_score = total_actual_load / total_vehicle_capacity
        capacity_utilization_score = float(capacity_utilization_score*100);

        return {
            "vendor_id": vendor_id,
            "metric": "capacity_utilization_rate",
            "score": round(capacity_utilization_score, 4),
            "raw_data": {
                "total_vehicle_capacity": total_vehicle_capacity,
                "total_actual_load": total_actual_load,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except ZeroDivisionError:
        return {
            "vendor_id": vendor_id,
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": "Division by zero: total_vehicle_capacity is zero",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except ValueError as ve:
        return {
            "vendor_id": vendor_id,
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": str(ve),
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }

    except Exception as e:
        return {
            "vendor_id": vendor_id,
            "metric": "capacity_utilization_rate",
            "score": 0.0,
            "raw_data": None,
            "error": f"Unexpected error: {str(e)}",
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
