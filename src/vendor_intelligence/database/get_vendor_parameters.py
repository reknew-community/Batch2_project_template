from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import asyncio


async def get_vendor_parameters(vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session
    ):

    sql = text("""
                CALL sp_get_vendor_performance_kpis(:vendor_id, :start_date, :end_date) 
               """)

    vendor_paramenters = db.execute(sql, {
            "vendor_id": vendor_id,
            "start_date": start_date,
            "end_date": end_date
        }).mappings().all()
    
    return vendor_paramenters