from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, time
from typing import Optional, List
from vendor_intelligence.database import get_db
from vendor_intelligence.services.vendor_performance_engine import calculate_vendor_performance
from vendor_intelligence.services.job_scheduler_service import start_scheduler
from vendor_intelligence.services.job_scheduler_service import run_stored_procedure
from vendor_intelligence.database.get_vendor_performance import fetch_vendor_performance_range
from vendor_intelligence.schemas.vendor_performance_schema import VendorPerformanceResponse
from vendor_intelligence.services.vendor_recommendation import get_vendors_recommendation
from vendor_intelligence.services.vendor_performance_summary import get_vendor_performance_scorecard

# scheduler = None

# @asynccontextmanager
# async def lifespan(app: FastAPI, db: Session = Depends(get_db)):
#     global scheduler
#     scheduler = start_scheduler(db)
#     print("App starting")

#     yield
#     if scheduler:
#         scheduler.shutdown()
#     print("App shutting down")

app = FastAPI()

def normalize_date_range(start_date, end_date):
    """
    Convert plain date inputs to datetime range:
    - start_date -> 00:00:00
    - end_date   -> 23:59:59.999999
    If inputs are already datetime, keep them unchanged.
    """
    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, time.min)

    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, time.max)

    return start_date, end_date

@app.get(
    "/vendors/{vendor_id}/scorecard",
    response_model=List[VendorPerformanceResponse]
)
async def vendor_performance_scorecard(
    vendor_id: int,
    days: Optional[int] = Query(None, description="If date range isn't mentioned by default it will 30 days"),
    db: Session = Depends(get_db)
):
    scorecard_values = get_vendor_performance_scorecard(vendor_id=vendor_id, days=days, db=db)

    return scorecard_values

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

    start_date, end_date = normalize_date_range(start_date, end_date)

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
    
@app.get("/vendors/dayscheduler")
async def run_daily_scheduler(db: Session = Depends(get_db)): 
    insertion_message = await run_stored_procedure(db)
    return insertion_message

@app.get("/vendors/recommend")
async def search_recommendation(
    from_city: str,
    to_city: str,
    shipment_weight: float,
    # shipment_date: date,
    db: Session = Depends(get_db)
):
    values = await get_vendors_recommendation(
        from_city,
        to_city,
        shipment_weight,
        # shipment_date,
        db
    )

    return values