import asyncio
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal, engine
from models.resort import Resort
from models import Base

async def import_resorts_from_csv():
    """Import resorts from CSV file."""
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Get existing resorts to avoid duplicates
        stmt = select(Resort)
        result = await session.execute(stmt)
        existing_resorts = result.scalars().all()
        existing_names = {resort.name for resort in existing_resorts}
        
        print(f"Found {len(existing_resorts)} existing resorts")
        
        # Read CSV file
        with open('resorts_clean.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            new_resorts = []
            for row in csv_reader:
                # Skip if resort already exists
                if row['name'] in existing_names:
                    continue
                
                # Parse amenities (pipe-separated)
                amenities = [amenity.strip() for amenity in row['amenities'].split('|')]
                
                # Parse images (comma-separated)
                images = [img.strip() for img in row['images'].split(',')]
                
                # Create resort object
                resort = Resort(
                    name=row['name'],
                    description=f"Luxury {row['type']} in {row['city']}, {row['country']} with {', '.join(amenities[:3])}",
                    type=row['type'],
                    address=row['address'],
                    city=row['city'],
                    country=row['country'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    star_rating=min(int(row['star_rating']), 5),  # Cap at 5 stars
                    price_per_night=float(row['price_per_night']),
                    total_rooms=int(row['room_availability']),
                    available_rooms=int(row['room_availability']),
                    amenities=amenities,
                    images=images,
                    is_active=True
                )
                
                new_resorts.append(resort)
        
        # Add new resorts to database
        if new_resorts:
            for resort in new_resorts:
                session.add(resort)
            
            await session.commit()
            print(f"Successfully imported {len(new_resorts)} new resorts!")
            print(f"Total resorts: {len(existing_resorts) + len(new_resorts)}")
        else:
            print("No new resorts to import (all already exist)")

if __name__ == "__main__":
    asyncio.run(import_resorts_from_csv())
