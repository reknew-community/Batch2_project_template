from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime
from typing import Dict, Any


# from vendor_intelligence.models.trip import Trip

def get_cost_per_kg(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    try:
        query = """
            SELECT SUM(total_cost) AS aggr_total_cost, SUM(weight_kg) AS aggr_weight_kg
            FROM trips_test tt 
            WHERE tt.vendor_id = :vendor_id AND 
                booking_date >= :start_date AND
                booking_date <= : end_data
            GROUP BY tt.vendor_id 
        """

        vendor_cost_per_kg_data = db.execute(query, 
                          {
                              "vendor_id": vendor_id,
                              "start_date": start_date,
                              "end_date": end_date
                            }).fetchall()
        
        total_cost = vendor_cost_per_kg_data.aggr_total_cost
        weight_kg = vendor_cost_per_kg_data.aggr_weight_kg

        cost_per_keg = round(total_cost/weight_kg, 2);

        result = {
            'vendor_id': vendor_id,
            'metric': 'cost_per_kg',
            'score': round(cost_per_keg, 2),
            'raw_data': {
                'total_cost': total_cost,
                'weight_kg': weight_kg,
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
            'metric': 'cost_per_kg',
            'score': 0.0,
            'raw_data': None,
            'error': str(e),
            'calculated_at': datetime.now().isoformat(),
            'success': False
        }