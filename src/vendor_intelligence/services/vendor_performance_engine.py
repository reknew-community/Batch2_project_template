from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio
from vendor_intelligence.core.config import settings
from vendor_intelligence.calculators.ontime_pickup_calculator import calculate_ontime_pickup_rate
from vendor_intelligence.calculators.ontime_delivery_calculator import calculate_ontime_delivery_rate
from vendor_intelligence.calculators.cost_per_kg_calculator import calculate_cost_competitiveness
from vendor_intelligence.calculators.exception_rate_calculator import calculate_exception_rate
from vendor_intelligence.calculators.pod_compliance_calculator import calculate_pod_compliance_rate
from vendor_intelligence.calculators.calculate_capacity_utilization_rate import calculate_capacity_utilization_rate


async def calculate_vendor_performance(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:

    results = await asyncio.gather(
        #On-time Pickup - Venu
        calculate_ontime_pickup_rate(vendor_id, start_date, end_date, db),
        
        # On-time Delivery - Harika
        calculate_ontime_delivery_rate(vendor_id, start_date, end_date, db),
        
        # Cost per Kg - Trilok
        #calculate_cost_competitiveness(vendor_id, start_date, end_date, db),
        
        #Exception Rate - Siva
        #calculate_exception_rate(vendor_id, start_date, end_date, db),
        
        #POD Compliance - Harish
        #calculate_pod_compliance_rate(vendor_id, start_date, end_date, db),

        #Capacity Utilization - Venu
        #calculate_capacity_utilization_rate(vendor_id, start_date, end_date, db)

    )
    
    # Unpack results from each calculator
    pickup_result = results[0]
    delivery_result = results[1]
    #cost_result = results[2]
    #exception_result = results[3]
    #pod_result = results[4]  
    #capacity_result = results[5]

#Extracting Scores from Each Calculator
    
    pickup_score = pickup_result.get('score', 0.0)
    delivery_score = delivery_result.get('score', 0.0)
    #cost_score = cost_result.get('score', 0.0)
    #exception_score = exception_result.get('score', 0.0)
    #capacity_score = capacity_result.get('score', 0.0)
   # pod_score = pod_result.get('score', 0.0)
   
    
    # Get weights from config
    w_delivery = settings.WEIGHT_ONTIME_DELIVERY          # 0.30 (30%)
    w_cost = settings.WEIGHT_COST_COMPETITIVENESS         # 0.25 (25%)
    w_exception = settings.WEIGHT_EXCEPTION_RATE          # 0.20 (20%)
    w_capacity = settings.WEIGHT_CAPACITY_UTILIZATION     # 0.15 (15%)
    w_pod = settings.WEIGHT_POD_COMPLIANCE                # 0.10 (10%)
    
    # Calculate weighted final score
    final_score = (
        delivery_score * w_delivery +
        0 * w_cost +
        0 * w_exception +
        0 * w_capacity + 
        0 * w_pod
    )
    
    # STEP 5: Build Scorecard Response
    scorecard = {
        'vendor_id': vendor_id,
        'calculation_period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        },
        'individual_scores': {
            'ontime_pickup': pickup_score,
            'ontime_delivery': delivery_score,
            'cost_competitiveness': 0,
            'exception_rate': 0,
            'pod_compliance': 0,
            'capacity_utilization': 0
        },
        'Vendor_Performance_Score': round(final_score, 2),
        'calculated_at': datetime.now().isoformat()
    }
    
    return scorecard


