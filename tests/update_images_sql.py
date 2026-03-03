"""
Direct SQL script to update database with real local images.
Fast and reliable database update.
"""

import json
import os
import glob
from sqlalchemy import create_engine, text

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

# Image settings
IMAGES_DIR = "static/images"

def get_local_image_mapping():
    """Create mapping of destination names to local images."""
    
    print("🔍 Scanning local images...")
    
    # Get all local images
    image_files = glob.glob(os.path.join(IMAGES_DIR, "*.jpg"))
    
    # Create mapping: destination_name -> [image_urls]
    image_mapping = {}
    
    for image_file in image_files:
        filename = os.path.basename(image_file)
        
        # Extract destination name and index
        if '_' in filename:
            parts = filename.replace('.jpg', '').split('_')
            if len(parts) >= 2:
                try:
                    # Last part is the index
                    index = int(parts[-1])
                    # Everything before that is the destination name
                    destination_name = '_'.join(parts[:-1]).replace('_', ' ')
                    
                    # Add to mapping
                    if destination_name not in image_mapping:
                        image_mapping[destination_name] = []
                    
                    # Ensure the list has enough slots
                    while len(image_mapping[destination_name]) <= index:
                        image_mapping[destination_name].append(None)
                    
                    image_mapping[destination_name][index] = f"/static/images/{filename}"
                    
                except ValueError:
                    # If index parsing fails, treat as single image
                    destination_name = filename.replace('.jpg', '').replace('_', ' ')
                    image_mapping[destination_name] = [f"/static/images/{filename}"]
    
    # Remove None values and sort
    for destination_name in image_mapping:
        image_mapping[destination_name] = [
            url for url in image_mapping[destination_name] if url is not None
        ]
    
    print(f"📁 Found {len(image_mapping)} destinations with local images")
    return image_mapping

def update_database_with_sql():
    """Update database using direct SQL."""
    
    print("🚀 Updating Database with Local Images...")
    print("=" * 50)
    
    # Get local image mapping
    image_mapping = get_local_image_mapping()
    
    if not image_mapping:
        print("❌ No local images found!")
        return
    
    # Create sync engine
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    
    with sync_engine.connect() as connection:
        updated_count = 0
        
        # Get all destinations
        result = connection.execute(text("SELECT id, name FROM destinations ORDER BY id"))
        destinations = result.fetchall()
        
        print(f"📍 Processing {len(destinations)} destinations")
        
        for destination_id, destination_name in destinations:
            print(f"\n🔍 Processing: {destination_name} (ID: {destination_id})")
            
            # Try to find matching images
            matched_images = None
            
            # Direct match
            if destination_name in image_mapping:
                matched_images = image_mapping[destination_name]
                print(f"   ✅ Direct match found: {len(matched_images)} images")
            
            # Partial match (try variations)
            else:
                # Try different name variations
                variations = [
                    destination_name,
                    destination_name.replace(',', ''),
                    destination_name.replace('-', ' '),
                    destination_name.split(',')[0],  # First part before comma
                    destination_name.split(' - ')[0],  # First part before dash
                ]
                
                for variation in variations:
                    if variation in image_mapping:
                        matched_images = image_mapping[variation]
                        print(f"   ✅ Partial match found: {len(matched_images)} images")
                        break
            
            # If no match, create placeholder
            if not matched_images:
                safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "").replace("-", "_")
                matched_images = [f"/static/images/placeholder-{safe_name}.jpg"]
                print(f"   📝 Using placeholder: {matched_images[0]}")
            
            # Update database
            update_stmt = text("""
                UPDATE destinations 
                SET images = :image_urls 
                WHERE id = :destination_id
            """)
            
            connection.execute(update_stmt, {
                "image_urls": json.dumps(matched_images),
                "destination_id": destination_id
            })
            
            print(f"   📸 Updated with: {matched_images}")
            updated_count += 1
        
        # Commit all changes
        connection.commit()
        print(f"\n🎉 Successfully updated {updated_count} destinations!")

def show_update_preview():
    """Show what will be updated without actually updating."""
    
    print("📋 Update Preview (No Changes Made)")
    print("=" * 50)
    
    # Get local image mapping
    image_mapping = get_local_image_mapping()
    
    # Create sync engine
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    
    with sync_engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM destinations ORDER BY id LIMIT 15"))
        destinations = result.fetchall()
        
        print(f"📍 Preview for first {len(destinations)} destinations:")
        
        for destination_id, destination_name in destinations:
            print(f"\n🏝️ {destination_name} (ID: {destination_id})")
            
            # Find matching images
            matched_images = None
            
            if destination_name in image_mapping:
                matched_images = image_mapping[destination_name]
                print(f"   ✅ Direct match: {len(matched_images)} images")
            else:
                safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "").replace("-", "_")
                matched_images = [f"/static/images/placeholder-{safe_name}.jpg"]
                print(f"   📝 Placeholder: {matched_images[0]}")
            
            print(f"   📸 Will update to: {matched_images}")

def create_backup():
    """Create a backup of current images data."""
    
    print("💾 Creating backup...")
    
    # Create sync engine
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    
    with sync_engine.connect() as connection:
        result = connection.execute(text("SELECT id, name, images FROM destinations ORDER BY id"))
        destinations = result.fetchall()
        
        backup_file = "database_images_backup.json"
        backup_data = []
        
        for destination_id, destination_name, images_data in destinations:
            backup_data.append({
                "id": destination_id,
                "name": destination_name,
                "images": images_data
            })
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup saved to {backup_file}")

def main():
    """Main function."""
    
    print("🚀 Direct SQL Image Updater")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Preview updates (no changes)
2. Create backup
3. Update database with local images
4. All (backup → preview → update)
5. Exit

Enter choice (1-5): """)
    
    if choice == "1":
        show_update_preview()
    elif choice == "2":
        create_backup()
    elif choice == "3":
        update_database_with_sql()
    elif choice == "4":
        create_backup()
        show_update_preview()
        update_database_with_sql()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
