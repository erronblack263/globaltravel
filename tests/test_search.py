"""
Simple test script to isolate the search endpoint issue.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text
from models.destination import Destination

async def test_search():
    """Test the search functionality directly."""
    
    # Create database connection
    engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost/globaltravel")
    
    async with AsyncSession(engine) as session:
        try:
            # Simple test query
            query = select(Destination).where(Destination.is_active == True)
            result = await session.execute(query)
            destinations = result.scalars().all()
            
            print(f"Found {len(destinations)} destinations")
            for dest in destinations[:3]:  # Show first 3
                print(f"  - {dest.name} ({dest.city}, {dest.country})")
            
            return [{"id": d.id, "name": d.name} for d in destinations]
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_search())
    print("Result:", result)
