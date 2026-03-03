import asyncio
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal, engine
from models.destination import Destination
from models import Base

async def import_from_csv():
    """Import destinations from CSV file."""
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Get existing destinations to avoid duplicates
        stmt = select(Destination)
        result = await session.execute(stmt)
        existing_destinations = result.scalars().all()
        existing_names = {dest.name for dest in existing_destinations}
        
        print(f"Found {len(existing_destinations)} existing destinations")
        
        # Read CSV file
        with open('destinations_clean.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            new_destinations = []
            for row in csv_reader:
                # Skip if destination already exists
                if row['name'] in existing_names:
                    continue
                
                # Parse images (comma-separated)
                images = [img.strip() for img in row['images'].split(',')]
                
                # Create destination object
                destination = Destination(
                    name=row['name'],
                    description=row['description'],
                    type=row['type'],
                    address=f"{row['city']}, {row['country']}",
                    city=row['city'],
                    country=row['country'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    entry_fee=float(row['entry_fee']),
                    visiting_hours=row['visiting_hours'],
                    best_time_to_visit=row['best_time_to_visit'],
                    images=images,
                    is_active=True
                )
                
                new_destinations.append(destination)
        
        # Add new destinations to database
        if new_destinations:
            for destination in new_destinations:
                session.add(destination)
            
            await session.commit()
            print(f"Successfully imported {len(new_destinations)} new destinations!")
            print(f"Total destinations: {len(existing_destinations) + len(new_destinations)}")
        else:
            print("No new destinations to import (all already exist)")

if __name__ == "__main__":
    asyncio.run(import_from_csv())
