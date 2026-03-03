"""
Simple synchronous script to download real images for destinations from Unsplash API.
Uses sync SQLAlchemy and requests.
"""

import requests
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

# Unsplash API configuration  
UNSPLASH_ACCESS_KEY = "VMv4dQtsdQ6iORyRYEUZZu7NtSc12z3X-Cu-iyFshEI"
UNSPLASH_BASE_URL = "https://api.unsplash.com"

# Image settings
IMAGES_DIR = "static/images"

def get_unsplash_images(destination_name, count=3):
    """Download images for a destination from Unsplash."""
    
    search_query = f"{destination_name} travel landscape"
    
    try:
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
        
        response = requests.get(search_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"❌ Error searching for {destination_name}: {response.status_code}")
            return []
                
    except Exception as e:
        print(f"❌ Exception searching for {destination_name}: {str(e)}")
        return []


def download_image(photo_info, destination_name, index):
    """Download a single image."""
    
    try:
        download_url = photo_info["urls"]["regular"]
        
        safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "")
        filename = f"{safe_name}_{index}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        response = requests.get(download_url)
        if response.status_code == 200:
            content = response.content
            
            with open(filepath, "wb") as f:
                f.write(content)
            
            print(f"✅ Downloaded: {filename}")
            return f"/static/images/{filename}"
        else:
            print(f"❌ Failed to download {filename}: {response.status_code}")
            return None
                
    except Exception as e:
        print(f"❌ Exception downloading {destination_name} image {index}: {str(e)}")
        return None


def update_destination_images(destination_id, image_urls):
    """Update destination with new image URLs."""
    
    try:
        stmt = text("""
            UPDATE destinations 
            SET images = :image_urls 
            WHERE id = :destination_id
        """)
        
        session.execute(stmt, {
            "image_urls": image_urls,
            "destination_id": destination_id
        })
        session.commit()
        
        print(f"✅ Updated destination {destination_id} with {len(image_urls)} images")
        
    except Exception as e:
        print(f"❌ Failed to update destination {destination_id}: {str(e)}")


def download_all_destination_images():
    """Download images for all destinations."""
    
    print("🖼️  Starting destination image download...")
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    if not UNSPLASH_ACCESS_KEY:
        print("❌ Unsplash API key not set")
        return
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Get all destinations
        stmt = text("SELECT id, name FROM destinations")
        result = session.execute(stmt)
        destinations = result.fetchall()
        
        print(f"📍 Found {len(destinations)} destinations")
        
        for destination in destinations:
            destination_id, destination_name = destination
            print(f"\n🔍 Processing: {destination_name}")
            
            photos = get_unsplash_images(destination_name, count=3)
            
            if photos:
                image_urls = []
                for i, photo in enumerate(photos):
                    image_url = download_image(photo, destination_name, i)
                    if image_url:
                        image_urls.append(image_url)
                
                if image_urls:
                    update_destination_images(destination_id, image_urls)
                
                import time
                time.sleep(2)
            else:
                print(f"❌ No images found for {destination_name}")
    
    finally:
        session.close()
    
    print("\n🎉 Image download completed!")


def create_placeholder_images():
    """Create placeholder images if Unsplash API is not available."""
    
    print("🖼️  Creating placeholder images...")
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        destinations = [
            "Hawaiian Paradise", "Maldives Island", "Santorini Greece", 
            "Paris France", "Tokyo Japan", "Iceland Golden Circle",
            "Victoria Falls", "Machu Picchu", "Dubai UAE", "New York USA"
        ]
        
        for dest_name in destinations:
            safe_name = dest_name.replace(" ", "_").replace(",", "").replace("'", "")
            placeholder_url = f"/static/images/placeholder-{safe_name}.jpg"
            
            stmt = text("""
                UPDATE destinations 
                SET images = :image_urls 
                WHERE name ILIKE :dest_name
            """)
            
            session.execute(stmt, {
                "image_urls": [placeholder_url],
                "dest_name": f"%{dest_name}%"
            })
            
            print(f"✅ Set placeholder for: {dest_name}")
        
        session.commit()
    
    finally:
        session.close()
    
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
