"""
Check how many unique cities are in destinations database.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, func, distinct
from models.destination import Destination

async def check_cities():
    """Check unique cities in destinations."""
    
    # Create database connection
    engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost/globaltravel")
    
    async with AsyncSession(engine) as session:
        try:
            # Count unique cities
            city_count_query = select(func.count(distinct(Destination.city))).where(Destination.is_active == True)
            city_count_result = await session.execute(city_count_query)
            total_cities = city_count_result.scalar()
            
            # Get all unique cities
            cities_query = select(distinct(Destination.city)).where(Destination.is_active == True).order_by(Destination.city)
            cities_result = await session.execute(cities_query)
            cities = [row[0] for row in cities_result.fetchall()]
            
            print(f"Total unique cities: {total_cities}")
            print(f"Cities: {cities}")
            
            return {
                "total_cities": total_cities,
                "cities": cities
            }
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(check_cities())
    print("Result:", result)
