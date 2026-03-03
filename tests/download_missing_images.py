"""
Smart script to download only missing destination images.
Skips already downloaded images and only downloads missing ones.
"""

import requests
import os
import glob
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

# Unsplash API configuration  
UNSPLASH_ACCESS_KEY = "VMv4dQtsdQ6iORyRYEUZZu7NtSc12z3X-Cu-iyFshEI"
UNSPLASH_BASE_URL = "https://api.unsplash.com"

# Image settings
IMAGES_DIR = "static/images"

def get_existing_images():
    """Get list of already downloaded images."""
    try:
        image_files = glob.glob(os.path.join(IMAGES_DIR, "*.jpg"))
        return set([os.path.basename(f) for f in image_files])
    except:
        return set()

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
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"❌ Error searching for {destination_name}: {response.status_code}")
            return []
                
    except Exception as e:
        print(f"❌ Exception searching for {destination_name}: {str(e)}")
        return []


def download_image(photo_info, destination_name, index, existing_images):
    """Download a single image if not already exists."""
    
    try:
        safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "")
        filename = f"{safe_name}_{index}.jpg"
        
        # Skip if already exists
        if filename in existing_images:
            print(f"⏭️ Skipping {filename} (already exists)")
            return f"/static/images/{filename}"
        
        download_url = photo_info["urls"]["regular"]
        filepath = os.path.join(IMAGES_DIR, filename)
        
        response = requests.get(download_url, timeout=10)
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
        sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
        Session = sessionmaker(bind=sync_engine)
        session = Session()
        
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
        session.close()
        
        print(f"✅ Updated destination {destination_id} with {len(image_urls)} images")
        
    except Exception as e:
        print(f"❌ Failed to update destination {destination_id}: {str(e)}")


def download_missing_images():
    """Download only missing images for destinations."""
    
    print("🖼️  Downloading Missing Destination Images...")
    print("=" * 50)
    
    # Get existing images
    existing_images = get_existing_images()
    print(f"📁 Found {len(existing_images)} existing images")
    
    # Create images directory
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
            
            # Get images from Unsplash
            photos = get_unsplash_images(destination_name, count=3)
            
            if photos:
                # Download images (skipping existing)
                image_urls = []
                for i, photo in enumerate(photos):
                    image_url = download_image(photo, destination_name, i, existing_images)
                    if image_url:
                        image_urls.append(image_url)
                
                # Update destination in database
                if image_urls:
                    update_destination_images(destination_id, image_urls)
                
                # Rate limiting
                import time
                time.sleep(1)
            else:
                print(f"❌ No images found for {destination_name}")
    
    finally:
        session.close()
    
    print("\n🎉 Missing image download completed!")


def redownload_all_images():
    """Force redownload all images (ignoring existing)."""
    
    print("🔄 Redownloading All Destination Images...")
    print("=" * 50)
    
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
            
            # Get images from Unsplash
            photos = get_unsplash_images(destination_name, count=3)
            
            if photos:
                # Download images (force redownload)
                image_urls = []
                for i, photo in enumerate(photos):
                    image_url = download_image(photo, destination_name, i, set())  # Empty set = force download
                    if image_url:
                        image_urls.append(image_url)
                
                # Update destination in database
                if image_urls:
                    update_destination_images(destination_id, image_urls)
                
                # Rate limiting
                import time
                time.sleep(1)
            else:
                print(f"❌ No images found for {destination_name}")
    
    finally:
        session.close()
    
    print("\n🎉 Redownload completed!")


def main():
    """Main function."""
    
    print("🖼️  Smart Destination Image Downloader")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Download only missing images (skip existing)
2. Force redownload all images
3. Exit

Enter choice (1-3): """)
    
    if choice == "1":
        download_missing_images()
    elif choice == "2":
        redownload_all_images()
    else:
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
