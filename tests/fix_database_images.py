"""
Script to fix database image formats.
Converts external URLs and text descriptions to proper local image URLs.
"""

import json
import os
import glob
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

# Image settings
IMAGES_DIR = "static/images"

def get_existing_local_images():
    """Get list of existing local image files."""
    try:
        image_files = glob.glob(os.path.join(IMAGES_DIR, "*.jpg"))
        return set([os.path.basename(f) for f in image_files])
    except:
        return set()

def fix_database_images():
    """Fix all database image records to use proper local URLs."""
    
    print("🔧 Fixing Database Image Formats...")
    print("=" * 50)
    
    # Get existing local images
    existing_images = get_existing_local_images()
    print(f"📁 Found {len(existing_images)} local images")
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Get all destinations
        stmt = text("SELECT id, name, images FROM destinations ORDER BY id")
        result = session.execute(stmt)
        destinations = result.fetchall()
        
        print(f"📍 Processing {len(destinations)} destinations")
        
        fixed_count = 0
        
        for destination in destinations:
            destination_id, destination_name, images_data = destination
            
            print(f"\n🔍 Processing: {destination_name} (ID: {destination_id})")
            
            # Check if images data is valid JSON
            if not images_data:
                print("   ❌ No images data - adding placeholder")
                new_images = create_placeholder_images(destination_name)
            else:
                try:
                    # Try to parse as JSON
                    images = json.loads(images_data)
                    
                    if isinstance(images, list):
                        # Check if it's external URLs or local URLs
                        if images and isinstance(images[0], str):
                            if images[0].startswith('http'):
                                print("   🔄 Converting external URLs to local")
                                new_images = create_local_image_urls(destination_name)
                            elif images[0].startswith('/static/'):
                                print("   ✅ Already has local URLs")
                                continue  # Skip this one
                            else:
                                print("   🔄 Converting text description to local URLs")
                                new_images = create_local_image_urls(destination_name)
                        else:
                            print("   🔄 Invalid format - creating local URLs")
                            new_images = create_local_image_urls(destination_name)
                    else:
                        print("   🔄 Not a list - creating local URLs")
                        new_images = create_local_image_urls(destination_name)
                        
                except json.JSONDecodeError:
                    print("   🔄 Invalid JSON - creating local URLs")
                    new_images = create_local_image_urls(destination_name)
            
            # Update the database
            update_stmt = text("""
                UPDATE destinations 
                SET images = :image_urls 
                WHERE id = :destination_id
            """)
            
            session.execute(update_stmt, {
                "image_urls": json.dumps(new_images),
                "destination_id": destination_id
            })
            
            print(f"   ✅ Updated with: {new_images}")
            fixed_count += 1
        
        session.commit()
        print(f"\n🎉 Fixed {fixed_count} destinations!")
    
    finally:
        session.close()

def create_local_image_urls(destination_name):
    """Create local image URLs for a destination."""
    
    safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "").replace("-", "_")
    
    # Check if local images exist
    existing_images = get_existing_local_images()
    
    # Find existing images for this destination
    local_urls = []
    for i in range(3):  # Check for 0, 1, 2
        filename = f"{safe_name}_{i}.jpg"
        if filename in existing_images:
            local_urls.append(f"/static/images/{filename}")
    
    if local_urls:
        return local_urls
    else:
        # Return placeholder if no local images found
        return [f"/static/images/placeholder-{safe_name}.jpg"]

def create_placeholder_images(destination_name):
    """Create placeholder image URLs for a destination."""
    
    safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "").replace("-", "_")
    return [f"/static/images/placeholder-{safe_name}.jpg"]

def show_current_status():
    """Show current database status before fixing."""
    
    print("📊 Current Database Status")
    print("=" * 50)
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Get all destinations
        stmt = text("SELECT id, name, images FROM destinations ORDER BY id LIMIT 10")
        result = session.execute(stmt)
        destinations = result.fetchall()
        
        print(f"📍 Sample of {len(destinations)} destinations:")
        
        for destination in destinations:
            destination_id, destination_name, images_data = destination
            
            print(f"\n🏝️ {destination_name} (ID: {destination_id})")
            
            if not images_data:
                print("   📸 No images")
            else:
                try:
                    images = json.loads(images_data)
                    if isinstance(images, list) and images:
                        first_image = images[0]
                        if isinstance(first_image, str):
                            if first_image.startswith('http'):
                                print(f"   📸 External URLs: {len(images)} images")
                                print(f"   📸 Sample: {first_image[:50]}...")
                            elif first_image.startswith('/static/'):
                                print(f"   📸 Local URLs: {len(images)} images")
                                print(f"   📸 Sample: {first_image}")
                            else:
                                print(f"   📸 Text/Other: {first_image[:50]}...")
                        else:
                            print(f"   📸 Invalid format")
                    else:
                        print(f"   📸 Not a list")
                except:
                    print(f"   📸 Invalid JSON: {str(images_data)[:50]}...")
    
    finally:
        session.close()

def main():
    """Main function."""
    
    print("🔧 Database Image Format Fixer")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Show current status (sample)
2. Fix all database image formats
3. Both (show then fix)
4. Exit

Enter choice (1-4): """)
    
    if choice == "1":
        show_current_status()
    elif choice == "2":
        fix_database_images()
    elif choice == "3":
        show_current_status()
        fix_database_images()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
