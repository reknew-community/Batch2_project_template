from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text
import pytz
from vendor_intelligence.database.get_vendor_parameters import get_vendor_parameters
from vendor_intelligence.services.vendor_performance_engine import calculate_vendor_performance
from vendor_intelligence.database.vendor_scores_insertion import insert_scores_into_vendor_performance_DB
from datetime import date, datetime, timedelta, time
from decimal import Decimal

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


async def run_stored_procedure(db):
    print("Running stored procedure...")
    # Call your DB stored procedure here

    #SQL query to fetch the vendor ids to run loop
    sql_to_get_vendor_ids = text("""
                SELECT id FROM vendors
        """)
    
    #executing the sql query and storing the ids in the list
    vendor_ids_list = db.execute(sql_to_get_vendor_ids).all()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    start_date, end_date = normalize_date_range(start_date, end_date)

    print("Start date:",start_date)
    print("End date",end_date)

    flag = 0

    for id in vendor_ids_list:

        v_id = id[0]

        vendor_performance_score = await calculate_vendor_performance(v_id, start_date, end_date, db)

        vendor_id = int(vendor_performance_score['vendor_id'])

        calculated_date = datetime.fromisoformat(
            vendor_performance_score['calculated_at']
        ).date()
        period_type = "Monthly"

        # ---- Calculation Parameters ----
        calc_params = vendor_performance_score.get('calculation_parameters', {})

        total_trips = int(calc_params.get('total_trips', 0))
        completed_trips = 0
        cancelled_trips = 0

        ontime_pickups = int(calc_params.get('ontime_pickups', 0))
        ontime_deliveries = int(calc_params.get('ontime_deliveries', 0))

        total_exceptions = int(calc_params.get('total_exceptions', 0))


        # ---- Individual Scores ----
        individual_scores = vendor_performance_score.get('individual_scores', {})

        ontime_pickup_rate = Decimal(individual_scores.get('ontime_pickup', 0))
        ontime_delivery_rate = Decimal(individual_scores.get('ontime_delivery', 0))

        exception_rate = Decimal(individual_scores.get('exception_rate', 0))
        avg_cost_per_kg = Decimal(individual_scores.get('cost_competitiveness', 0))
        avg_capacity_utilization_pct = Decimal(individual_scores.get('capacity_utilization', 0))
        pod_compliance_rate = Decimal(individual_scores.get('pod_compliance', 0))

        performance_score = Decimal(
            vendor_performance_score.get('Vendor_Performance_Score', 0)
        )

        created_ts = datetime.fromisoformat(
            vendor_performance_score['calculated_at']
        ).date()
        updated_ts = datetime.fromisoformat(
            vendor_performance_score['calculated_at']
        ).date()

        avg_cost_per_trip = 0

        execution_message = insert_scores_into_vendor_performance_DB(vendor_id,
                                                calculated_date,
                                                period_type,
                                                total_trips,
                                                completed_trips,
                                                cancelled_trips,
                                                ontime_pickups,
                                                ontime_deliveries,
                                                ontime_pickup_rate,
                                                ontime_delivery_rate,
                                                total_exceptions,
                                                exception_rate,
                                                avg_cost_per_kg,
                                                avg_cost_per_trip,
                                                avg_capacity_utilization_pct,
                                                pod_compliance_rate,
                                                performance_score,
                                                created_ts,
                                                updated_ts,
                                                db)
        
        if execution_message == "success":
            print("Insertion into the vendor performance table success!!!")
        else:
            print("Faced an exception. Here it is: ",execution_message)
            print("For vendor",id)
            flag =1

    if flag == 1:
        print("Insertion faild for few vendors. Check above for the ids")
    else:
        print("Insetion successful for all the vendors")

def start_scheduler(db):
    ist = pytz.timezone("Asia/Kolkata")
    scheduler = BackgroundScheduler(timezone=ist)

    scheduler.add_job(
        run_stored_procedure(db),
        CronTrigger(hour=23, minute=0),
        args=[db],
    )

    scheduler.start()
    return scheduler