from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def get_cost_per_kg(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:

    try:
        query = text("""
            SELECT 
                SUM(total_cost) AS aggr_total_cost,
                SUM(weight_kg) AS aggr_weight_kg
            FROM shipments
            WHERE vendor_id = :vendor_id
              AND booking_date >= :start_date
              AND booking_date <= :end_date
            GROUP BY vendor_id
        """)

        query_market_rate = text("""
            SELECT 
                SUM(total_cost) AS aggr_total_cost,
                SUM(weight_kg) AS aggr_weight_kg
            FROM shipments
            WHERE booking_date >= :start_date
              AND booking_date <= :end_date
        """)

        row = db.execute(
            query,
            {
                "vendor_id": vendor_id,
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()

        row_market_rate_data = db.execute(
            query_market_rate,
            {
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()

        if not row or not row.aggr_weight_kg:
            return {
                "vendor_id": vendor_id,
                "metric": "cost_per_kg",
                "score": 0.0,
                "success": False,
                "error": "No data available"
            }

        total_cost_vendor = row.aggr_total_cost
        weight_kg_vendor = row.aggr_weight_kg

        total_cost_market = row_market_rate_data.aggr_total_cost
        weight_kg_market = row_market_rate_data.aggr_weight_kg

        cost_per_kg = float(round(total_cost_vendor / weight_kg_vendor, 2))

        market_rate_per_kg = float(round(total_cost_market / weight_kg_market, 2))

        cost_competitiveness_score = 0

        if market_rate_per_kg == 0:
            cost_competitiveness_score = 50 
        
        cost_ratio = cost_per_kg / market_rate_per_kg

        if cost_ratio <= 0.8:
            cost_competitiveness_score = 100
        elif cost_ratio <= 1.0:
            cost_competitiveness_score = 75 + (1.0 - cost_ratio) * 125
        elif cost_ratio <= 1.5:
            cost_competitiveness_score = 75 - (cost_ratio - 1.0) * 120
        else:
            cost_competitiveness_score = 0

        cost_competitiveness_score = round(max(0, min(100, cost_competitiveness_score)),2)

        return {
            "vendor_id": vendor_id,
            "metric": "cost_per_kg",
            "score": cost_competitiveness_score,
            "raw_data": {
                "total_cost": total_cost_vendor,
                "weight_kg": weight_kg_vendor,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            },
            "calculated_at": datetime.now().isoformat(),
            "success": True
        }

    except Exception as e:
        raise  
