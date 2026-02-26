from vendor_intelligence.database.get_vendor_recommendation import fetch_vendor_list
from vendor_intelligence.schemas.vendor_data_schema import VendorResponse
from fastapi import HTTPException, status
from vendor_intelligence.services.vendor_performance_summary import get_vendor_performance_scorecard
from vendor_intelligence.schemas.vendor_performance_schema import VendorPerformanceResponse

async def get_vendors_recommendation(
        from_city,
        to_city,
        shipment_weight,
        db
    ):

    if from_city == to_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From city and To city cannot be the same."
        )
    
    # if shipment_date < datetime.now().date():
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Shipment date must be today or a future date."
    #     )
    
    if shipment_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shipment weight must be greater than zero."
        )

    #Fetching the vendor details
    vendor_list_by_route = await fetch_vendor_list(from_city, to_city, db)    

    vendors = [
        VendorResponse(**vendor)
        for vendor in vendor_list_by_route
    ]

    #filtering the vendors based on the available capacity to ship
    filtered_vendors = [
        vendor
        for vendor in vendors
        if vendor.available_capacity >= shipment_weight
    ]

    #getting the performance scores of the vendors
    vendor_performance_scores = [
        get_vendor_performance_scorecard(int(vendor.id), 30, db)
        for vendor in filtered_vendors
    ]

    # vendor_performance_objects = [
    #     VendorPerformanceResponse(**perf[0])  
    #     for perf in vendor_performance_scores
    #     if len(perf) > 0               
    # ]

    vendor_with_scores = [
        {
            "vendor": vendor,
            "performance": VendorPerformanceResponse(**perf[0]) 
        }
        for vendor, perf in zip(filtered_vendors, vendor_performance_scores)
        if len(perf) > 0  
    ]

    vendor_with_scores_sorted = sorted(
        vendor_with_scores,
        key=lambda x: (
            -float(x["performance"].performance_score), 
            -float(x["performance"].avg_cost_per_kg)      
        )
    )

    # Step 3: Take top 3
    top_three = vendor_with_scores_sorted[:3]
    
    return top_three