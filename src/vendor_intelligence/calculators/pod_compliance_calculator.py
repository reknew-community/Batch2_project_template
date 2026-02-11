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
            SELECT 
                id,
                awb_id,
                assigned_vendor_id,
                actual_delivery_date,
                current_status,
                pod_uploaded,
                pod_upload_timestamp,
                signature_obtained
            FROM shipments
            WHERE assigned_vendor_id = :vendor_id
            AND current_status = 'DELIVERED'
            AND actual_delivery_date >= :start_date
            AND actual_delivery_date <= :end_date
        """)

        # Execute query and get all rows
        shipments = db.execute(sql, {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()

        # Step 2: Count total delivered shipments
        total_delivered = len(shipments)
        # Example: 150 shipments

        # Step 3: Count POD uploaded (where pod_uploaded = 1)
        pod_uploaded = sum(
            1 for shipment in shipments
            if shipment.pod_uploaded == 1
        )

        # Example: 143 shipments have POD

        # Step 4: Calculate POD missing
        pod_missing = total_delivered - pod_uploaded
        # Example: 150 - 143 = 7 missing

        # Step 5: Calculate POD compliance percentage
        if total_delivered > 0:
            score = (pod_uploaded / total_delivered) * 100
        else:
            score = 0.0
        # Example: (143 / 150) * 100 = 95.33%

        # Step 6: Return formatted result
        return {
            'vendor_id': vendor_id,
            'metric': 'pod_compliance',
            'score': round(score, 2),
            'raw_data': {
                'total_delivered': total_delivered,
                'pod_uploaded': pod_uploaded,
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