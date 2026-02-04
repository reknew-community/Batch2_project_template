from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime
from typing import Dict, Any

from vendor_intelligence.models.trip import Trip

async def calculate_ontime_delivery_rate(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:

    try:
        # Query all trips for this vendor in the date range
        trips = db.query(Trip).filter(
            Trip.vendor_id == vendor_id,
            Trip.scheduled_pickup_time >= start_date,
            Trip.scheduled_pickup_time <= end_date,
            Trip.actual_pickup_time.isnot(None)  # Only completed pickups
        ).all()
        
        # Count total pickups
        total_pickups = len(trips)
        
        # Count on-time pickups
        # On-time = actual_pickup_time <= scheduled_pickup_time
        ontime_pickups = sum(
            1 for trip in trips 
            if trip.actual_pickup_time <= trip.scheduled_pickup_time
        )
        
        # Count late pickups
        late_pickups = total_pickups - ontime_pickups
        # Calculate on-time pickup percentage     
        if total_pickups > 0:
            score = (ontime_pickups / total_pickups) * 100
        else:
            score = 0.0

        result = {
            'vendor_id': vendor_id,
            'metric': 'ontime_pickup',
            'score': round(score, 2),
            'raw_data': {
                'total_pickups': total_pickups,
                'ontime_pickups': ontime_pickups,
                'late_pickups': late_pickups,
                'ontime_percentage': round(score, 2),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            },
            'calculated_at': datetime.now().isoformat(),
            'success': True
        }
        
        return result
        
    except Exception as e:
        # Error handling
        return {
            'vendor_id': vendor_id,
            'metric': 'ontime_pickup',
            'score': 0.0,
            'raw_data': None,
            'error': str(e),
            'calculated_at': datetime.now().isoformat(),
            'success': False
        }