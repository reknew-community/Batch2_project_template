from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from vendor_intelligence.database import get_db
from vendor_intelligence.services.vendor_performance_engine import calculate_vendor_performance

app = FastAPI()

@app.get("/vendors/{vendor_id}/performance")
async def get_vendor_performance(
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    result = await calculate_vendor_performance(
        vendor_id=vendor_id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    return result
