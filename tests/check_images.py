import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.resort import Resort

async def check_image_urls():
    """Check what image URLs are in the database."""
    
    async with AsyncSessionLocal() as session:
        # Get all resorts with their images
        stmt = select(Resort)
        result = await session.execute(stmt)
        resorts = result.scalars().all()
        
        print(f"Found {len(resorts)} resorts")
        print("\nFirst 5 resorts and their image URLs:")
        
        for i, resort in enumerate(resorts[:5]):
            print(f"\n{i+1}. {resort.name}")
            print(f"   Images: {resort.images}")
        
        # Search for the specific URL
        target_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
        print(f"\n\nSearching for: {target_url}")
        
        found_resorts = []
        for resort in resorts:
            if resort.images and target_url in str(resort.images):
                found_resorts.append(resort)
        
        print(f"Found {len(found_resorts)} resorts with that URL:")
        for resort in found_resorts:
            print(f"  - {resort.name}")

if __name__ == "__main__":
    asyncio.run(check_image_urls())
