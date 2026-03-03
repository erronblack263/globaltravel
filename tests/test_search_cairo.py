"""
Test search for Cairo specifically.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text, and_, or_
from models.destination import Destination

async def test_cairo_search():
    """Test Cairo search specifically."""
    
    # Create database connection
    engine = create_async_engine("postgresql+asyncpg://postgres:12345678@localhost/globaltravel")
    
    async with AsyncSession(engine) as session:
        try:
            # Test the exact search logic from the endpoint
            name = "cairo"
            
            # Simple name search across multiple fields
            query = select(Destination).where(
                and_(
                    or_(
                        Destination.name.ilike(f"%{name}%"),
                        Destination.description.ilike(f"%{name}%"),
                        Destination.city.ilike(f"%{name}%"),
                        Destination.country.ilike(f"%{name}%"),
                        Destination.category.ilike(f"%{name}%"),
                        Destination.type.ilike(f"%{name}%")
                    ),
                    Destination.is_active == True
                )
            )
            
            result = await session.execute(query)
            destinations = result.scalars().all()
            
            print(f"Search for '{name}' found {len(destinations)} destinations:")
            for dest in destinations:
                print(f"  - {dest.name} (ID: {dest.id}, City: {dest.city}, Country: {dest.country})")
            
            return [{"id": d.id, "name": d.name, "city": d.city, "country": d.country} for d in destinations]
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_cairo_search())
    print("Result:", result)
