from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_pod_compliance_rate(
        total_delivered: int,
        pod_compliant_deliveries: int
) -> Dict[str, Any]:
    try:

        # Step 4: Calculate POD missing
        pod_missing = total_delivered - pod_compliant_deliveries

        # Step 5: Calculate POD compliance percentage
        if total_delivered > 0:
            score = (pod_compliant_deliveries / total_delivered) * 100
        else:
            score = 0.0

        # Step 6: Return formatted result
        return {
            'metric': 'pod_compliance',
            'score': round(score, 2),
            'raw_data': {
                'total_delivered': total_delivered,
                'pod_compliant_deliveries': pod_compliant_deliveries,
                'pod_missing': pod_missing,
                'pod_compliance_rate': round(score, 2)
            },
            'calculated_at': datetime.now().isoformat(),
            'success': True
        }

    except Exception as e:
        # Error handling
        return {
            'metric': 'pod_compliance',
            'score': 0.0,
            'raw_data': None,
            'error': str(e),
            'calculated_at': datetime.now().isoformat(),
            'success': False
        }