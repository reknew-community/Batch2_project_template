from sqlalchemy import text

async def fetch_vendor_list(from_city, to_city, db):
    # Safe because from_city and to_city are FastAPI query params (strings)
    # Strip any quotes to prevent injection
    from_city = from_city.replace('"', '').replace("'", '')
    to_city = to_city.replace('"', '').replace("'", '')

    sql_query = text(f"""
        SELECT * 
        FROM vendors 
        WHERE JSON_CONTAINS(service_areas, '["{from_city}", "{to_city}"]') AND is_active = 1
    """)

    result = db.execute(sql_query).mappings().all()

    return result