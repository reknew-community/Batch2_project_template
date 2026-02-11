from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_ontime_pickup_rate(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    try:
        sql = text("""SELECT
                   COUNT(*) AS total_pickups,
                   SUM(CASE WHEN t.actual_departure <= t.scheduled_departure THEN 1 ELSE 0 END) AS ontime_pickups 
                   FROM trips t
                   WHERE t.vendor_id = :vendor_id
                   AND t.scheduled_departure BETWEEN :start_date AND :end_date
                   AND t.status IN ('COMPLETED','IN_TRANSIT')
                   AND t.actual_departure IS NOT NULL
                   AND t.scheduled_departure IS NOT NULL""")

        row = db.execute(sql, {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchone()

        total_pickups = int(row.total_pickups or 0) if row else 0
        ontime_pickups = int(row.ontime_pickups or 0) if row else 0

        if total_pickups == 0:
            return {
                "vendor_id": vendor_id,
                "metric": "ontime_pickup",
                "score": 0.0,
                "raw_data": {
                    "total_pickups": 0,
                    "ontime_pickups": 0,
                    "ontime_percentage": 0.0,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                },
                "calculated_at": datetime.now().isoformat(),
                "success": True
            }

        ontime_percentage = (ontime_pickups / total_pickups) * 100.0
        score = round(ontime_percentage, 2)

        return {
            "vendor_id": vendor_id,
            "metric": "ontime_pickup",
            "score": score,
            "raw_data": {
                "total_pickups": total_pickups,
                "ontime_pickups": ontime_pickups,
                "ontime_percentage": score,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date.date() - start_date.date()).days + 1  # optional inclusive
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except Exception as e:
        return {
            "vendor_id": vendor_id,
            "metric": "ontime_pickup",
            "score": 0.0,
            "raw_data": None,
            "error": str(e),
            "error_type": type(e).__name__,
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
