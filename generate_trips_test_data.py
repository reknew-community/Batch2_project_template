import mysql.connector
from datetime import datetime, timedelta
import random

print("=" * 80)
print("TRIPS TEST DATA GENERATION SCRIPT")
print("Group 2 - Vendor Intelligence Project")
print("=" * 80)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
try:
    conn = mysql.connector.connect(
        host='157.180.28.78',
        port=3306,
        user='tbatch2',  # REPLACE WITH YOUR USERNAME
        password='tbatch2',  # REPLACE WITH YOUR PASSWORD
        database='tbatch2_db'
    )
    cursor = conn.cursor(dictionary=True)
    print("\n✅ Database connection successful!")
except Exception as e:
    print(f"\n❌ Database connection failed: {str(e)}")
    exit(1)

# ============================================================================
# FETCH MASTER DATA
# ============================================================================
print("\n" + "-" * 80)
print("FETCHING MASTER DATA")
print("-" * 80)

# Fetch vendors
cursor.execute("SELECT id, vendor_code, name FROM vendors_test WHERE is_active = TRUE ORDER BY id")
vendors = cursor.fetchall()
print(f"✅ Found {len(vendors)} active vendors")
for v in vendors:
    print(f"   {v['vendor_code']}: {v['name']}")

# Fetch hubs
cursor.execute("SELECT id, hub_code, city FROM hubs_test WHERE is_active = TRUE ORDER BY id")
hubs = cursor.fetchall()
print(f"\n✅ Found {len(hubs)} active hubs")
for h in hubs:
    print(f"   {h['hub_code']}: {h['city']}")

# Fetch customers
cursor.execute("SELECT id, customer_code, name FROM customers_test WHERE is_active = TRUE ORDER BY id")
customers = cursor.fetchall()
print(f"\n✅ Found {len(customers)} active customers")

# ============================================================================
# VENDOR PERFORMANCE PROFILES
# ============================================================================
print("\n" + "-" * 80)
print("VENDOR PERFORMANCE PROFILES")
print("-" * 80)

vendor_profiles = {
    1: {  # V-001 Swift Logistics - EXCELLENT
        'name': 'Swift Logistics',
        'trips': 40,
        'ontime_pickup': 0.90,
        'ontime_delivery': 0.92,
        'exception_rate': 0.05,
        'pod_rate': 0.95,
        'cost_factor': 0.93
    },
    2: {  # V-002 Express Freight - GOOD
        'name': 'Express Freight',
        'trips': 35,
        'ontime_pickup': 0.80,
        'ontime_delivery': 0.82,
        'exception_rate': 0.12,
        'pod_rate': 0.85,
        'cost_factor': 1.00
    },
    3: {  # V-003 Reliable Transport - AVERAGE
        'name': 'Reliable Transport',
        'trips': 38,
        'ontime_pickup': 0.70,
        'ontime_delivery': 0.72,
        'exception_rate': 0.20,
        'pod_rate': 0.75,
        'cost_factor': 1.07
    },
    4: {  # V-004 Budget Cargo - BELOW AVERAGE
        'name': 'Budget Cargo',
        'trips': 25,
        'ontime_pickup': 0.60,
        'ontime_delivery': 0.62,
        'exception_rate': 0.30,
        'pod_rate': 0.65,
        'cost_factor': 0.89
    },
    5: {  # V-005 Premium Express - PREMIUM
        'name': 'Premium Express',
        'trips': 45,
        'ontime_pickup': 0.95,
        'ontime_delivery': 0.96,
        'exception_rate': 0.03,
        'pod_rate': 0.98,
        'cost_factor': 1.22
    },
    6: {  # V-006 City Link - REGIONAL GOOD
        'name': 'City Link',
        'trips': 22,
        'ontime_pickup': 0.85,
        'ontime_delivery': 0.87,
        'exception_rate': 0.08,
        'pod_rate': 0.88,
        'cost_factor': 0.67
    },
    7: {  # V-007 Gateway Transport - MID-TIER
        'name': 'Gateway Transport',
        'trips': 30,
        'ontime_pickup': 0.75,
        'ontime_delivery': 0.77,
        'exception_rate': 0.15,
        'pod_rate': 0.80,
        'cost_factor': 0.98
    },
    8: {  # V-008 FastTrack - INCONSISTENT
        'name': 'FastTrack',
        'trips': 28,
        'ontime_pickup': 0.65,
        'ontime_delivery': 0.68,
        'exception_rate': 0.25,
        'pod_rate': 0.70,
        'cost_factor': 1.02
    },
    9: {  # V-009 NextGen - NEW
        'name': 'NextGen',
        'trips': 27,
        'ontime_pickup': 0.78,
        'ontime_delivery': 0.80,
        'exception_rate': 0.18,
        'pod_rate': 0.82,
        'cost_factor': 1.04
    }
}

for vendor_id, profile in vendor_profiles.items():
    print(f"Vendor {vendor_id} ({profile['name']}): "
          f"{profile['trips']} trips, "
          f"Pickup: {profile['ontime_pickup']*100:.0f}%, "
          f"Delivery: {profile['ontime_delivery']*100:.0f}%, "
          f"Exception: {profile['exception_rate']*100:.0f}%, "
          f"POD: {profile['pod_rate']*100:.0f}%")

# ============================================================================
# ROUTE DEFINITIONS WITH WEIGHTS
# ============================================================================
print("\n" + "-" * 80)
print("ROUTE CONFIGURATION")
print("-" * 80)

# Popular routes with higher weights
popular_routes = [
    ('Mumbai', 'Bangalore', 25),
    ('Delhi', 'Mumbai', 22),
    ('Bangalore', 'Chennai', 20),
    ('Mumbai', 'Pune', 18),
    ('Delhi', 'Jaipur', 15),
    ('Ahmedabad', 'Mumbai', 15),
    ('Hyderabad', 'Bangalore', 14),
    ('Chennai', 'Bangalore', 12),
    ('Kolkata', 'Delhi', 12),
    ('Mumbai', 'Delhi', 12),
]

print("Top 10 Popular Routes:")
for origin, dest, count in popular_routes:
    print(f"  {origin} → {dest}: {count} trips")

remaining_trips = 290 - sum([r[2] for r in popular_routes])
print(f"\nRemaining trips to distribute: {remaining_trips}")

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================
BASE_RATE_PER_KG = 45.00
PICKUP_GRACE_MINUTES = 30
DELIVERY_GRACE_MINUTES = 120

print("\n" + "-" * 80)
print("CALCULATION PARAMETERS")
print("-" * 80)
print(f"Base Rate: ₹{BASE_RATE_PER_KG}/kg")
print(f"Pickup Grace Period: {PICKUP_GRACE_MINUTES} minutes")
print(f"Delivery Grace Period: {DELIVERY_GRACE_MINUTES} minutes")

# Date range: Last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
print(f"Date Range: {start_date.date()} to {end_date.date()}")

# ============================================================================
# GENERATE TRIPS DATA
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING TRIPS DATA")
print("=" * 80)

trips_generated = 0
trips_data = []

# Generate trips for each vendor based on their profile
for vendor_id, profile in vendor_profiles.items():
    vendor_trips = profile['trips']
    
    print(f"\n📦 Generating {vendor_trips} trips for Vendor {vendor_id} ({profile['name']})...")
    
    for trip_num in range(vendor_trips):
        # Random customer
        customer = random.choice(customers)
        customer_id = customer['id']
        
        # Select origin and destination hubs (different hubs)
        origin_hub = random.choice(hubs)
        destination_hub = random.choice([h for h in hubs if h['id'] != origin_hub['id']])
        
        origin_hub_id = origin_hub['id']
        destination_hub_id = destination_hub['id']
        route_code = f"{origin_hub['city'][:3].upper()}-{destination_hub['city'][:3].upper()}"
        
        # Random booking date in last 30 days
        days_ago = random.randint(0, 30)
        booking_date = (end_date - timedelta(days=days_ago)).date()
        
        # Scheduled pickup time: 8 AM to 2 PM
        scheduled_pickup_time = datetime.combine(
            booking_date,
            datetime.min.time()
        ) + timedelta(
            hours=random.randint(8, 14),
            minutes=random.choice([0, 15, 30, 45])
        )
        
        # Scheduled delivery time: 18-36 hours after pickup
        scheduled_delivery_time = scheduled_pickup_time + timedelta(
            hours=random.randint(18, 36)
        )
        
        # ACTUAL PICKUP TIME (based on vendor profile)
        is_pickup_ontime = random.random() < profile['ontime_pickup']
        if is_pickup_ontime:
            # On-time: -15 to +30 minutes
            pickup_delay_minutes = random.randint(-15, 30)
        else:
            # Late: 45 minutes to 4 hours
            pickup_delay_minutes = random.randint(45, 240)
        
        actual_pickup_time = scheduled_pickup_time + timedelta(minutes=pickup_delay_minutes)
        
        # ACTUAL DELIVERY TIME (based on vendor profile)
        is_delivery_ontime = random.random() < profile['ontime_delivery']
        if is_delivery_ontime:
            # On-time: -30 to +120 minutes (within grace period)
            delivery_delay_minutes = random.randint(-30, 120)
        else:
            # Late: 3 to 12 hours
            delivery_delay_minutes = random.randint(180, 720)
        
        actual_delivery_time = scheduled_delivery_time + timedelta(minutes=delivery_delay_minutes)
        delivery_date = actual_delivery_time.date()
        
        # WEIGHT AND COST
        weight_kg = round(random.uniform(50, 2000), 2)
        cost_per_kg = BASE_RATE_PER_KG * profile['cost_factor'] * random.uniform(0.95, 1.05)
        total_cost = round(weight_kg * cost_per_kg, 2)
        cost_per_kg = round(cost_per_kg, 2)
        
        # EXCEPTION
        has_exception = random.random() < profile['exception_rate']
        if has_exception:
            # Exception type distribution: DELAY 70%, DAMAGE 20%, SHORT 8%, LOST 2%
            rand_val = random.random()
            if rand_val < 0.70:
                exception_type = 'DELAY'
            elif rand_val < 0.90:
                exception_type = 'DAMAGE'
            elif rand_val < 0.98:
                exception_type = 'SHORT'
            else:
                exception_type = 'LOST'
            
            exception_description = f"{exception_type} reported during transit"
            exception_reported_at = actual_delivery_time + timedelta(hours=random.randint(1, 3))
        else:
            exception_type = 'NONE'
            exception_description = None
            exception_reported_at = None
        
        # POD UPLOAD
        pod_uploaded = random.random() < profile['pod_rate']
        if pod_uploaded:
            pod_upload_timestamp = actual_delivery_time + timedelta(
                hours=random.randint(1, 24)
            )
            pod_url = f"https://pods.example.com/{booking_date.strftime('%Y%m%d')}/{trips_generated:04d}.pdf"
        else:
            pod_upload_timestamp = None
            pod_url = None
        
        # STATUS (all delivered)
        status = 'DELIVERED'
        
        # PRIORITY (80% standard, 15% express, 5% urgent)
        rand_priority = random.random()
        if rand_priority < 0.80:
            priority = 'STANDARD'
        elif rand_priority < 0.95:
            priority = 'EXPRESS'
        else:
            priority = 'URGENT'
        
        # SHIPMENT TYPE (60% parcel, 30% document, 10% cargo)
        rand_type = random.random()
        if rand_type < 0.60:
            shipment_type = 'PARCEL'
        elif rand_type < 0.90:
            shipment_type = 'DOCUMENT'
        else:
            shipment_type = 'CARGO'
        
        # AWB NUMBER
        awb_number = f"AWB{booking_date.strftime('%Y%m%d')}{trips_generated:04d}"
        
        # Store trip data
        trip_data = (
            awb_number, customer_id, vendor_id, origin_hub_id, destination_hub_id, route_code,
            scheduled_pickup_time, actual_pickup_time, scheduled_delivery_time, actual_delivery_time,
            weight_kg, total_cost, cost_per_kg, status, booking_date, delivery_date,
            has_exception, exception_type, exception_description, exception_reported_at,
            pod_uploaded, pod_upload_timestamp, pod_url, priority, shipment_type
        )
        
        trips_data.append(trip_data)
        trips_generated += 1
    
    print(f"   ✅ Generated {vendor_trips} trips for Vendor {vendor_id}")

# ============================================================================
# INSERT TRIPS INTO DATABASE
# ============================================================================
print("\n" + "=" * 80)
print("INSERTING TRIPS INTO DATABASE")
print("=" * 80)

insert_query = """
INSERT INTO trips_test 
(awb_number, customer_id, vendor_id, origin_hub_id, destination_hub_id, route_code,
 scheduled_pickup_time, actual_pickup_time, scheduled_delivery_time, actual_delivery_time,
 weight_kg, total_cost, cost_per_kg, status, booking_date, delivery_date,
 has_exception, exception_type, exception_description, exception_reported_at,
 pod_uploaded, pod_upload_timestamp, pod_url, priority, shipment_type)
VALUES 
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

inserted_count = 0
error_count = 0

for trip_data in trips_data:
    try:
        cursor.execute(insert_query, trip_data)
        inserted_count += 1
        
        if inserted_count % 50 == 0:
            print(f"  Inserted {inserted_count} trips...")
            
    except Exception as e:
        error_count += 1
        print(f"  ❌ Error inserting trip: {str(e)}")

# Commit all inserts
conn.commit()

print(f"\n✅ Successfully inserted {inserted_count} trips!")
if error_count > 0:
    print(f"⚠️  {error_count} errors occurred")

# ============================================================================
# VERIFICATION & STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("VERIFICATION & STATISTICS")
print("=" * 80)

# Total trips
cursor.execute("SELECT COUNT(*) as total FROM trips_test")
result = cursor.fetchone()
print(f"\n📊 Total trips in database: {result['total']}")

# Trips by vendor
print("\n📈 Trips by Vendor:")
cursor.execute("""
    SELECT v.vendor_code, v.name, COUNT(*) as trip_count
    FROM trips_test t
    JOIN vendors_test v ON t.vendor_id = v.id
    GROUP BY v.vendor_code, v.name
    ORDER BY v.id
""")
for row in cursor.fetchall():
    print(f"  {row['vendor_code']}: {row['trip_count']:3d} trips - {row['name']}")

# Trips by status
print("\n📦 Trips by Status:")
cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM trips_test
    GROUP BY status
""")
for row in cursor.fetchall():
    print(f"  {row['status']}: {row['count']} trips")

# Top 10 routes
print("\n🛣️  Top 10 Routes:")
cursor.execute("""
    SELECT route_code, COUNT(*) as trip_count
    FROM trips_test
    GROUP BY route_code
    ORDER BY trip_count DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"  {row['route_code']}: {row['trip_count']} trips")

# Exception summary
print("\n⚠️  Exception Summary:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_trips,
        SUM(CASE WHEN has_exception = TRUE THEN 1 ELSE 0 END) as trips_with_exceptions,
        ROUND((SUM(CASE WHEN has_exception = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as exception_rate
    FROM trips_test
""")
result = cursor.fetchone()
print(f"  Total Trips: {result['total_trips']}")
print(f"  Trips with Exceptions: {result['trips_with_exceptions']}")
print(f"  Overall Exception Rate: {result['exception_rate']}%")

# Exception types breakdown
cursor.execute("""
    SELECT 
        exception_type,
        COUNT(*) as count,
        ROUND((COUNT(*) / (SELECT COUNT(*) FROM trips_test WHERE has_exception = TRUE)) * 100, 2) as percentage
    FROM trips_test
    WHERE has_exception = TRUE
    GROUP BY exception_type
    ORDER BY count DESC
""")
print("\n  Exception Types Breakdown:")
for row in cursor.fetchall():
    print(f"    {row['exception_type']}: {row['count']} ({row['percentage']}%)")

# POD upload summary
print("\n📄 POD Upload Summary:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_deliveries,
        SUM(CASE WHEN pod_uploaded = TRUE THEN 1 ELSE 0 END) as pods_uploaded,
        ROUND((SUM(CASE WHEN pod_uploaded = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as pod_rate
    FROM trips_test
    WHERE status = 'DELIVERED'
""")
result = cursor.fetchone()
print(f"  Total Deliveries: {result['total_deliveries']}")
print(f"  PODs Uploaded: {result['pods_uploaded']}")
print(f"  Overall POD Upload Rate: {result['pod_rate']}%")

# Date range
print("\n📅 Date Range:")
cursor.execute("""
    SELECT 
        MIN(booking_date) as earliest_booking,
        MAX(booking_date) as latest_booking,
        MIN(delivery_date) as earliest_delivery,
        MAX(delivery_date) as latest_delivery
    FROM trips_test
""")
result = cursor.fetchone()
print(f"  Bookings: {result['earliest_booking']} to {result['latest_booking']}")
print(f"  Deliveries: {result['earliest_delivery']} to {result['latest_delivery']}")

# Weight and cost summary
print("\n💰 Weight & Cost Summary:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_trips,
        ROUND(SUM(weight_kg), 2) as total_weight,
        ROUND(AVG(weight_kg), 2) as avg_weight,
        ROUND(SUM(total_cost), 2) as total_revenue,
        ROUND(AVG(cost_per_kg), 2) as avg_cost_per_kg
    FROM trips_test
""")
result = cursor.fetchone()
print(f"  Total Weight: {result['total_weight']:,.2f} kg")
print(f"  Average Weight per Trip: {result['avg_weight']:.2f} kg")
print(f"  Total Revenue: ₹{result['total_revenue']:,.2f}")
print(f"  Average Cost per KG: ₹{result['avg_cost_per_kg']:.2f}")

# ============================================================================
# SAMPLE CALCULATION PREVIEW (for each calculator)
# ============================================================================
print("\n" + "=" * 80)
print("SAMPLE CALCULATIONS PREVIEW")
print("=" * 80)

# Venu's Calculator: On-time Pickup Rate for Vendor 1
print("\n👤 VENU - On-Time Pickup Rate (Vendor 1):")
cursor.execute("""
    SELECT 
        vendor_id,
        COUNT(*) as total_trips,
        SUM(CASE 
            WHEN actual_pickup_time <= DATE_ADD(scheduled_pickup_time, INTERVAL 30 MINUTE) 
            THEN 1 ELSE 0 
        END) as ontime_pickups,
        ROUND((SUM(CASE 
            WHEN actual_pickup_time <= DATE_ADD(scheduled_pickup_time, INTERVAL 30 MINUTE) 
            THEN 1 ELSE 0 
        END) / COUNT(*)) * 100, 2) as ontime_pickup_rate
    FROM trips_test
    WHERE vendor_id = 1
      AND status = 'DELIVERED'
      AND actual_pickup_time IS NOT NULL
    GROUP BY vendor_id
""")
result = cursor.fetchone()
if result:
    print(f"  Total Trips: {result['total_trips']}")
    print(f"  On-Time Pickups: {result['ontime_pickups']}")
    print(f"  On-Time Pickup Rate: {result['ontime_pickup_rate']}%")

# Harika's Calculator: On-time Delivery Rate for Vendor 1
print("\n👤 HARIKA - On-Time Delivery Rate (Vendor 1):")
cursor.execute("""
    SELECT 
        vendor_id,
        COUNT(*) as total_deliveries,
        SUM(CASE 
            WHEN actual_delivery_time <= DATE_ADD(scheduled_delivery_time, INTERVAL 120 MINUTE) 
            THEN 1 ELSE 0 
        END) as ontime_deliveries,
        ROUND((SUM(CASE 
            WHEN actual_delivery_time <= DATE_ADD(scheduled_delivery_time, INTERVAL 120 MINUTE) 
            THEN 1 ELSE 0 
        END) / COUNT(*)) * 100, 2) as ontime_delivery_rate
    FROM trips_test
    WHERE vendor_id = 1
      AND status = 'DELIVERED'
      AND actual_delivery_time IS NOT NULL
    GROUP BY vendor_id
""")
result = cursor.fetchone()
if result:
    print(f"  Total Deliveries: {result['total_deliveries']}")
    print(f"  On-Time Deliveries: {result['ontime_deliveries']}")
    print(f"  On-Time Delivery Rate: {result['ontime_delivery_rate']}%")

# Trilok's Calculator: Cost Per KG for Vendor 1
print("\n👤 TRILOK - Average Cost Per KG (Vendor 1):")
cursor.execute("""
    SELECT 
        vendor_id,
        COUNT(*) as total_trips,
        ROUND(SUM(total_cost), 2) as total_cost,
        ROUND(SUM(weight_kg), 2) as total_weight,
        ROUND(SUM(total_cost) / SUM(weight_kg), 2) as avg_cost_per_kg
    FROM trips_test
    WHERE vendor_id = 1
      AND status = 'DELIVERED'
      AND weight_kg > 0
    GROUP BY vendor_id
""")
result = cursor.fetchone()
if result:
    print(f"  Total Trips: {result['total_trips']}")
    print(f"  Total Cost: ₹{result['total_cost']:,.2f}")
    print(f"  Total Weight: {result['total_weight']:,.2f} kg")
    print(f"  Average Cost Per KG: ₹{result['avg_cost_per_kg']:.2f}")

# Siva's Calculator: Exception Rate for Vendor 1
print("\n👤 SIVA - Exception Rate (Vendor 1):")
cursor.execute("""
    SELECT 
        vendor_id,
        COUNT(*) as total_trips,
        SUM(CASE WHEN has_exception = TRUE THEN 1 ELSE 0 END) as total_exceptions,
        ROUND((SUM(CASE WHEN has_exception = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as exception_rate
    FROM trips_test
    WHERE vendor_id = 1
      AND status = 'DELIVERED'
    GROUP BY vendor_id
""")
result = cursor.fetchone()
if result:
    print(f"  Total Trips: {result['total_trips']}")
    print(f"  Total Exceptions: {result['total_exceptions']}")
    print(f"  Exception Rate: {result['exception_rate']}%")

# Harish's Calculator: POD Upload Compliance for Vendor 1
print("\n👤 HARISH - POD Upload Compliance (Vendor 1):")
cursor.execute("""
    SELECT 
        vendor_id,
        COUNT(*) as deliveries_completed,
        SUM(CASE WHEN pod_uploaded = TRUE THEN 1 ELSE 0 END) as pods_uploaded,
        ROUND((SUM(CASE WHEN pod_uploaded = TRUE THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as pod_upload_rate
    FROM trips_test
    WHERE vendor_id = 1
      AND status = 'DELIVERED'
    GROUP BY vendor_id
""")
result = cursor.fetchone()
if result:
    print(f"  Deliveries Completed: {result['deliveries_completed']}")
    print(f"  PODs Uploaded: {result['pods_uploaded']}")
    print(f"  POD Upload Rate: {result['pod_upload_rate']}%")

# ============================================================================
# CLEANUP
# ============================================================================
cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DATA GENERATION COMPLETE!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   - Total Trips Generated: {trips_generated}")
print(f"   - Date Range: Last 30 days")
print(f"   - All trips status: DELIVERED")
print(f"   - Ready for calculator testing!")
print("\n🎉 All team members can now start building their calculators!")
print("=" * 80)