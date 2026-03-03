import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from models.destination import Destination

async def check_entry_fees():
    """Check what entry fees are in the database."""
    
    async with AsyncSessionLocal() as session:
        # Get all destinations with their entry fees
        stmt = select(Destination).where(Destination.is_active == True)
        result = await session.execute(stmt)
        destinations = result.scalars().all()
        
        print(f"Found {len(destinations)} active destinations")
        
        # Show entry fee distribution
        fee_ranges = {
            "Free (0)": 0,
            "Under $10": 0,
            "$10-$25": 0,
            "$25-$50": 0,
            "$50-$100": 0,
            "Over $100": 0
        }
        
        print("\nFirst 10 destinations and their entry fees:")
        for i, dest in enumerate(destinations[:10]):
            print(f"{i+1}. {dest.name}: ${dest.entry_fee}")
            
            # Categorize by fee
            fee = dest.entry_fee
            if fee == 0:
                fee_ranges["Free (0)"] += 1
            elif fee < 10:
                fee_ranges["Under $10"] += 1
            elif fee < 25:
                fee_ranges["$10-$25"] += 1
            elif fee < 50:
                fee_ranges["$25-$50"] += 1
            elif fee < 100:
                fee_ranges["$50-$100"] += 1
            else:
                fee_ranges["Over $100"] += 1
        
        print(f"\nEntry fee distribution:")
        for range_name, count in fee_ranges.items():
            print(f"  {range_name}: {count} destinations")
        
        # Test the specific query for $90
        print(f"\n\nTesting query for entry_fee <= 90:")
        test_stmt = select(Destination).where(
            Destination.entry_fee <= 90,
            Destination.is_active == True
        ).order_by(Destination.entry_fee.asc())
        
        test_result = await session.execute(test_stmt)
        matching_dests = test_result.scalars().all()
        
        print(f"Found {len(matching_dests)} destinations with entry_fee <= 90")
        
        if matching_dests:
            print("First 5 matching destinations:")
            for i, dest in enumerate(matching_dests[:5]):
                print(f"  {i+1}. {dest.name}: ${dest.entry_fee}")

if __name__ == "__main__":
    asyncio.run(check_entry_fees())
