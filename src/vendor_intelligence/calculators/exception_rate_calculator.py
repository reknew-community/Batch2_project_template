from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_exception_rate(
    total_shipments: int,
    exception_shipments: int
) -> Dict[str, Any]:
    try:
        exception_rate = float((exception_shipments/total_shipments)*100)

        result = {
            "metric": "exception_rate",
            "score": round(exception_rate, 2),
            "raw_data": {
                "total_shipments": total_shipments,
                "total_exceptions": exception_shipments,
                "rates": {
                    "overall_rate": round(exception_rate, 2),
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

        return result

    except Exception as e:
        return {
            "metric": "exception_rate",
            "score": 0.0,
            "raw_data": None,
            "error": str(e),
            "calculated_at": datetime.now().isoformat(),
            "success": False
        }
