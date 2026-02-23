from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
import asyncio
from vendor_intelligence.core.config import settings
from vendor_intelligence.calculators.ontime_pickup_calculator import calculate_ontime_pickup_rate
from vendor_intelligence.calculators.ontime_delivery_calculator import calculate_ontime_delivery_rate
from vendor_intelligence.calculators.cost_per_kg_calculator import calculate_cost_competitiveness
from vendor_intelligence.calculators.exception_rate_calculator import calculate_exception_rate
from vendor_intelligence.calculators.pod_compliance_calculator import calculate_pod_compliance_rate
from vendor_intelligence.calculators.calculate_capacity_utilization_rate import calculate_capacity_utilization_rate
from vendor_intelligence.database.get_vendor_parameters import get_vendor_parameters


async def calculate_vendor_performance(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    
    vendor_parameters = get_vendor_parameters(vendor_id, start_date, end_date, db)

    print(vendor_parameters)

    results = await asyncio.gather(
        #On-time Pickup - Venu
        calculate_ontime_pickup_rate(
            int(vendor_parameters[0].get('total_completed_trips')),
            int(vendor_parameters[0].get('ontime_pickups'))
            ),
        
        # On-time Delivery - Venu
        calculate_ontime_delivery_rate(
            int(vendor_parameters[0].get('total_completed_trips')),
            int(vendor_parameters[0].get('ontime_deliveries'))
            ),
        
        # Cost per Kg - Trilok
        calculate_cost_competitiveness(
            float(vendor_parameters[0].get('total_cost')), 
            float(vendor_parameters[0].get('total_weight')), 
            float(vendor_parameters[0].get('aggr_total_cost')),
            float(vendor_parameters[0].get('aggr_weight_kg'))
            ),
        
        #Exception Rate - Siva
        calculate_exception_rate(
            int(vendor_parameters[0].get('total_shipments')),
            int(vendor_parameters[0].get('exception_shipments'))
            ),
        
        #POD Compliance - Harish
        calculate_pod_compliance_rate(
            int(vendor_parameters[0].get('total_shipments')),
            int(vendor_parameters[0].get('pod_compliant_shipments'))
            ),

        #Capacity Utilization - Trilok
        calculate_capacity_utilization_rate(
            float(vendor_parameters[0].get('total_vehicle_capacity')), 
            float(vendor_parameters[0].get('total_actual_load'))
            )

    )
    
    # Unpack results from each calculator
    # We expect 6 values in results (pickup, delivery, cost, exception, pod, capacity).
    # To avoid errors when results has less than 6 items, we add default None values.
    # Then we take only the first 6 items and unpack them into variables safely.
    pickup_result, delivery_result, cost_result,exception_result, pod_result, capacity_result = (results + [None]*6)[:6]

    #Extracting Scores from Each Calculator
    pickup_score = pickup_result.get('score', 0.0)
    delivery_score = delivery_result.get('score', 0.0)
    cost_score = cost_result.get('score', 0.0)
    exception_score = exception_result.get('score', 0.0)
    capacity_score = capacity_result.get('score', 0.0)
    pod_score = pod_result.get('score', 0.0)
   
    # Get weights from config
    w_delivery = settings.WEIGHT_ONTIME_DELIVERY          # 0.30 (30%)
    w_cost = settings.WEIGHT_COST_COMPETITIVENESS         # 0.25 (25%)
    w_exception = settings.WEIGHT_EXCEPTION_RATE          # 0.20 (20%)
    w_capacity = settings.WEIGHT_CAPACITY_UTILIZATION     # 0.15 (15%)
    w_pod = settings.WEIGHT_POD_COMPLIANCE                # 0.10 (10%)
    
    # Calculate weighted final score
    final_score = (
        delivery_score * w_delivery +
        cost_score * w_cost +
        exception_score * w_exception +
        capacity_score * w_capacity + 
        pod_score * w_pod
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
            'cost_competitiveness': cost_score,
            'exception_rate': exception_score,
            'pod_compliance': pod_score,
            'capacity_utilization': capacity_score
        },
        'Vendor_Performance_Score': round(final_score, 2),
        'calculated_at': datetime.now().isoformat()
    }  
    return scorecard


