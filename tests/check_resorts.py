import asyncio
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.resort import Resort

async def check_resorts():
    """Check what resorts were imported vs what's in CSV."""
    
    async with AsyncSessionLocal() as session:
        # Get imported resorts
        stmt = select(Resort)
        result = await session.execute(stmt)
        imported_resorts = result.scalars().all()
        imported_names = {resort.name for resort in imported_resorts}
        
        print(f"Found {len(imported_resorts)} imported resorts")
        
        # Read CSV file
        with open('resorts_clean.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            csv_names = []
            for row in csv_reader:
                csv_names.append(row['name'])
        
        print(f"CSV has {len(csv_names)} resorts")
        
        # Find missing ones
        missing_names = [name for name in csv_names if name not in imported_names]
        print(f"Missing {len(missing_names)} resorts:")
        for name in missing_names:
            print(f"  - {name}")
        
        # Show imported resorts
        print(f"\nImported resorts:")
        for resort in imported_resorts:
            print(f"  - {resort.name} ({resort.star_rating} stars, ${resort.price_per_night}/night)")

if __name__ == "__main__":
    asyncio.run(check_resorts())
