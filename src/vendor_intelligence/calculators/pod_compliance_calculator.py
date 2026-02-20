from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

async def calculate_pod_compliance_rate(
        vendor_id: int,
        start_date: datetime,
        end_date: datetime,
        db: Session
) -> Dict[str, Any]:
    try:
        # Step 1: Query database for ALL delivered shipments
        sql = text("""
                   SELECT COUNT(*) AS total_deliveries,
                   SUM(CASE WHEN s.pod_uploaded = 1 THEN 1 ELSE 0 END) AS pod_compliant_deliveries
                   FROM shipments s
                   WHERE s.assigned_vendor_id = :vendor_id
                   AND s.current_status = 'DELIVERED'
                   AND s.actual_delivery_date BETWEEN :start_date AND :end_date""")

        # Execute query and get all rows
        shipments = db.execute(sql, {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()

        # Count total delivered shipments and Pod Compliant deliveries
        total_delivered = int(shipments[0].total_deliveries or 0) if shipments else 0
        pod_compliant_deliveries = int(shipments[0].pod_compliant_deliveries or 0) if shipments else 0

        # Step 4: Calculate POD missing
        pod_missing = total_delivered - pod_compliant_deliveries

        # Step 5: Calculate POD compliance percentage
        if total_delivered > 0:
            score = (pod_compliant_deliveries / total_delivered) * 100
        else:
            score = 0.0

        # Step 6: Return formatted result
        return {
            'vendor_id': vendor_id,
            'metric': 'pod_compliance',
            'score': round(score, 2),
            'raw_data': {
                'total_delivered': total_delivered,
                'pod_compliant_deliveries': pod_compliant_deliveries,
                'pod_missing': pod_missing,
                'pod_compliance_rate': round(score, 2),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            },
            'calculated_at': datetime.now().isoformat(),
            'success': True
        }

    except Exception as e:
        # Error handling
        return {
            'vendor_id': vendor_id,
            'metric': 'pod_compliance',
            'score': 0.0,
            'raw_data': None,
            'error': str(e),
            'calculated_at': datetime.now().isoformat(),
            'success': False
        }