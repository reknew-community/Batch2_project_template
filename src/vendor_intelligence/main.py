from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from vendor_intelligence.database import get_db
from vendor_intelligence.services.vendor_performance_engine import calculate_vendor_performance

app = FastAPI()

@app.get("/vendors/{vendor_id}/performance")
async def get_vendor_performance(
    vendor_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date (YYYY-MM-DD). Defaults to 30 days ago if not provided."),
    end_date: Optional[datetime] = Query(None, description="End date (YYYY-MM-DD). Defaults to today if not provided."),
    db: Session = Depends(get_db)
):
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.now()
    
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date"
        ) 
    
    #limit maximum date range to prevent heavy queries( Adding this for Extra safety)
    date_diff = (end_date - start_date).days
    if date_diff > 365:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 365 days"
        )
    
    try:
        result = await calculate_vendor_performance(
            vendor_id=vendor_id,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    