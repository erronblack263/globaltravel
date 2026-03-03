"""
Script to download real images for destinations from Unsplash API.
This will fetch high-quality travel images for each destination in your database.
"""

import asyncio
import requests
import os
from sqlalchemy import select, text
from core.database import engine
from models.destination import Destination
from core.config import settings

# Unsplash API configuration
UNSPLASH_ACCESS_KEY = settings.UNSPLASH_ACCESS_KEY if hasattr(settings, 'UNSPLASH_ACCESS_KEY') else "VMv4dQtsdQ6iORyRYEUZZu7NtSc12z3X-Cu-iyFshEI"
UNSPLASH_BASE_URL = "https://api.unsplash.com"

# Image settings
IMAGE_SIZE = "800x600"  # Standard size for web
IMAGES_DIR = "static/images"

async def get_unsplash_images(session, destination_name, count=3):
    """Download images for a destination from Unsplash."""
    
    # Search query based on destination name
    search_query = f"{destination_name} travel landscape"
    
    try:
        # Search for photos
        search_url = f"{UNSPLASH_BASE_URL}/search/photos"
        params = {
            "query": search_query,
            "per_page": count,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        async with session.get(search_url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("results", [])
            else:
                print(f"❌ Error searching for {destination_name}: {response.status}")
                return []
                
    except Exception as e:
        print(f"❌ Exception searching for {destination_name}: {str(e)}")
        return []

async def download_image(session, photo_info, destination_name, index):
    """Download a single image."""
    
    try:
        # Get download URL (requires proper attribution)
        download_url = photo_info["urls"]["regular"]
        
        # Create filename
        safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "")
        filename = f"{safe_name}_{index}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Download the image
        async with session.get(download_url) as response:
            if response.status == 200:
                content = await response.read()
                
                # Save to file
                with open(filepath, "wb") as f:
                    f.write(content)
                
                print(f"✅ Downloaded: {filename}")
                return f"/static/images/{filename}"
            else:
                print(f"❌ Failed to download {filename}: {response.status}")
                return None
                
    except Exception as e:
        print(f"❌ Exception downloading {destination_name} image {index}: {str(e)}")
        return None

async def update_destination_images(destination_id, image_urls, db):
    """Update destination with new image URLs."""
    
    try:
        stmt = text("""
            UPDATE destinations 
            SET images = :image_urls 
            WHERE id = :destination_id
        """)
        
        await db.execute(stmt, {
            "image_urls": image_urls,
            "destination_id": destination_id
        })
        await db.commit()
        
        print(f"✅ Updated destination {destination_id} with {len(image_urls)} images")
        
    except Exception as e:
        print(f"❌ Failed to update destination {destination_id}: {str(e)}")

def download_all_destination_images():
    """Download images for all destinations."""
    
    print("🖼️  Starting destination image download...")
    
    # Create images directory if it doesn't exist
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    # Check if Unsplash API key is set
    if not UNSPLASH_ACCESS_KEY:
        print("❌ Unsplash API key not set")
        return
    
    with engine.begin() as db:
        # Get all destinations
        stmt = select(Destination)
        result = db.execute(stmt)
        destinations = result.scalars().all()
        
        print(f"📍 Found {len(destinations)} destinations")
        
        for destination in destinations:
            print(f"\n🔍 Processing: {destination.name}")
            
            # Get images from Unsplash
            photos = get_unsplash_images(destination.name, count=3)
            
            if photos:
                # Download images
                image_urls = []
                for i, photo in enumerate(photos):
                    image_url = download_image(photo, destination.name, i)
                    if image_url:
                        image_urls.append(image_url)
                
                # Update destination in database
                if image_urls:
                    update_destination_images(destination.id, image_urls, db)
                
                # Rate limiting (Unsplash free tier: 50 requests/hour)
                import time
                time.sleep(2)
            else:
                print(f"❌ No images found for {destination.name}")
    
    print("\n🎉 Image download completed!")

def create_placeholder_images():
    """Create placeholder images if Unsplash API is not available."""
    
    print("🖼️  Creating placeholder images...")
    
    # Create images directory
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    # Common destination names
    destinations = [
        "Hawaiian Paradise", "Maldives Island", "Santorini Greece", 
        "Paris France", "Tokyo Japan", "Iceland Golden Circle",
        "Victoria Falls", "Machu Picchu", "Dubai UAE", "New York USA"
    ]
    
    with engine.begin() as db:
        for dest_name in destinations:
            # Create placeholder filename
            safe_name = dest_name.replace(" ", "_").replace(",", "").replace("'", "")
            placeholder_url = f"/static/images/placeholder-{safe_name}.jpg"
            
            # Update destination with placeholder
            stmt = text("""
                UPDATE destinations 
                SET images = :image_urls 
                WHERE name ILIKE :dest_name
            """)
            
            db.execute(stmt, {
                "image_urls": [placeholder_url],
                "dest_name": f"%{dest_name}%"
            })
            
            print(f"✅ Set placeholder for: {dest_name}")
        
        db.commit()
    
    print("🎉 Placeholder images configured!")

def main():
    """Main function."""
    
    print("🖼️  Destination Image Setup")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Download real images from Unsplash (requires API key)
2. Use placeholder images
3. Exit

Enter choice (1-3): """)
    
    if choice == "1":
        download_all_destination_images()
    elif choice == "2":
        create_placeholder_images()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
