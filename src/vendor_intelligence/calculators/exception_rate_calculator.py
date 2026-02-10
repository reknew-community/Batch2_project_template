from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime
from typing import Dict, Any

from vendor_intelligence.models.trip import Trip

async def calculate_exception_rate(
 vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
) -> Dict[str, Any]:
    score = 0.0

    return {'score': round(score, 2)}