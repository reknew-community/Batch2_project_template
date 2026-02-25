from sqlalchemy import text

def insert_scores_into_vendor_performance_DB(
    vendor_id,
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
    pod_compliance_rate,
    performance_score,
    created_ts,
    updated_ts,
    db
):
    try:
        insertion_sql = text("""
            INSERT INTO vendor_performance(
                vendor_id, 
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
            ) 
            VALUES(
                :vendor_id, 
                :calculated_date, 
                :period_type,
                :total_trips,
                :completed_trips,
                :cancelled_trips,
                :ontime_pickups,
                :ontime_pickup_rate,
                :ontime_deliveries,
                :ontime_delivery_rate,
                :total_exceptions,
                :exception_rate,
                :avg_cost_per_kg,
                :avg_cost_per_trip,
                :avg_capacity_utilization_pct,
                :performance_score,
                :created_ts,
                :updated_ts
            )
        """)

        db.execute(insertion_sql, {
            "vendor_id": vendor_id,
            "calculated_date": calculated_date,
            "period_type": period_type,
            "total_trips": total_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "ontime_pickups": ontime_pickups,
            "ontime_pickup_rate": ontime_pickup_rate,
            "ontime_deliveries": ontime_deliveries,
            "ontime_delivery_rate": ontime_delivery_rate,
            "total_exceptions": total_exceptions,
            "exception_rate": exception_rate,
            "avg_cost_per_kg": avg_cost_per_kg,
            "avg_cost_per_trip": avg_cost_per_trip,
            "avg_capacity_utilization_pct": avg_capacity_utilization_pct,
            "performance_score": performance_score,
            "created_ts": created_ts,
            "updated_ts": updated_ts,
        })

        db.commit()

        return "success"

    except Exception as e:
        db.rollback()
        return str(e)