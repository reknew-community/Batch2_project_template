from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, time, date
from typing import Dict, Any

from vendor_intelligence.models.trip import Trip

async def calculate_ontime_pickup_rate(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    try:
        # Build query with database-level aggregation
        sql = text("""
            SELECT
                   COUNT(*) AS total_pickups,
                   SUM(CASE
                   WHEN t.status IN ('COMPLETED','IN_TRANSIT')
                   AND t.actual_departure IS NOT NULL
                   AND t.scheduled_departure IS NOT NULL
                   AND t.actual_departure <= t.scheduled_departure
                   THEN 1 ELSE 0
                   END) AS ontime_pickups FROM trips t
                   WHERE t.vendor_id = :vendor_id
                   AND t.scheduled_departure >= :start_date
                   AND t.scheduled_departure <= :end_date
                   AND t.status IN ('COMPLETED','IN_TRANSIT')
                   AND t.actual_departure IS NOT NULL
                   AND t.scheduled_departure IS NOT NULL""")        
        params = {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Execute query
        result = db.execute(sql, params).fetchone()
        
        # Handle no data case
        if not result or result.total_pickups == 0:
            return {
                'vendor_id': vendor_id,
                'metric': 'ontime_pickup',
                'score': 0.0,
                'raw_data': {
                    'total_pickups': 0,
                    'ontime_pickups': 0,
                    'ontime_percentage': 0.0,
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                },
                'calculated_at': datetime.now().isoformat(),
                'success': True
            }
        
        # Extract values with safe defaults
        total_pickups = result.total_pickups or 0
        ontime_pickups = result.ontime_pickups or 0
        
        # Ontime percentage calculation
        ontime_percentage = (ontime_pickups / total_pickups * 100) if total_pickups > 0 else 0.0
        
        # Score is the on-time percentage
        score = round(ontime_percentage, 2)
        
        response = {
            'vendor_id': vendor_id,
            'metric': 'ontime_pickup',
            'score': score,
            'raw_data': {
                'total_pickups': total_pickups,
                'ontime_pickups': ontime_pickups,
                'ontime_percentage': round(ontime_percentage, 2),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                }
            },
            'calculated_at': datetime.now().isoformat(),
            'success': True
        }
        
        return response
        
    except Exception as e:
        # Return error response
        return {
            'vendor_id': vendor_id,
            'metric': 'ontime_pickup',
            'score': 0.0,
            'raw_data': None,
            'error': str(e),
            'error_type': type(e).__name__,
            'calculated_at': datetime.now().isoformat(),
            'success': False
        }
