from typing import Optional
from datetime import datetime, timedelta
from vendor_intelligence.database.get_vendor_performance import fetch_vendor_performance_range

def get_vendor_performance_scorecard(
        vendor_id: int,
        days: Optional[int],
        db,
):
    today = datetime.now().date()

    if days == None:
        days = 30

    end_date = today - timedelta(days=0)   
    start_date = today - timedelta(days=days)

    values = fetch_vendor_performance_range(
        vendor_id,
        start_date,
        end_date,
        db
    )

    return values
