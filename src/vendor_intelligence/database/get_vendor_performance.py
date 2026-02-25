from sqlalchemy import text

def fetch_vendor_performance_range(vendor_id, start_date, end_date, db):
    sql = text("""
        SELECT vendor_id, 
                calculated_date, 
                period_type,
                total_trips,
                completed_trips,
                cancelled_trips,
                ontime_pickups,
                ontime_pickup_rate,
                ontime_deliveries,
                ontime_delivery_rate,
                total_exceptions,
                exception_rate,
                avg_cost_per_kg,
                avg_cost_per_trip,
                avg_capacity_utilization_pct,
                performance_score,
                created_ts,
                updated_ts
        FROM vendor_performance
        WHERE vendor_id = :vendor_id
        AND calculated_date BETWEEN :start_date AND :end_date
        ORDER BY calculated_date DESC
    """)

    return db.execute(
        sql,
        {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date,
        }
    ).mappings().all()

    return result