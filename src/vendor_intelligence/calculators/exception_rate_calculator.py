from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_exception_rate(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    try:
        sql = text("""SELECT COUNT(*) AS total_shipments,
                   SUM(CASE WHEN s.has_exception = 1 THEN 1 ELSE 0 END) AS exception_shipments,
                   ROUND((SUM(CASE WHEN s.has_exception = 1 THEN 1 ELSE 0 END) * 100.0)/ NULLIF(COUNT(*), 0),2) AS exception_rate_pct 
                   FROM shipments s 
                   WHERE s.assigned_vendor_id = :vendor_id
                   AND s.booking_date >= :start_date
                   AND s.booking_date <= :end_date
                   AND s.current_status IN ('DELIVERED','IN_TRANSIT','OUT_FOR_DELIVERY');
                   """)

        row = db.execute(sql, {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchone()

        total_shipments = int(row.total_shipments or 0)
        exception_shipments = int(row.exception_shipments or 0)
        exception_rate = float(row.exception_rate_pct or 0.0)

        result = {
            "vendor_id": vendor_id,
            "metric": "exception_rate",
            "score": round(exception_rate, 2),
            "raw_data": {
                "total_shipments": total_shipments,
                "total_exceptions": exception_shipments,
                "rates": {
                    "overall_rate": round(exception_rate, 2),
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

        return result

    except Exception as e:
        return {
            "vendor_id": vendor_id,
            "metric": "exception_rate",
            "score": 0.0,
            "raw_data": None,
            "error": str(e),
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
