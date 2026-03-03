"""
Script to check what images are stored in the database.
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

def check_database_images():
    """Check what images are stored in the database."""
    
    print("🔍 Checking Database Images...")
    print("=" * 50)
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Get all destinations with their images
        stmt = text("""
            SELECT id, name, images 
            FROM destinations 
            WHERE images IS NOT NULL 
            ORDER BY id
        """)
        
        result = session.execute(stmt)
        destinations = result.fetchall()
        
        print(f"📍 Found {len(destinations)} destinations with images")
        
        for destination in destinations:
            destination_id, destination_name, images_json = destination
            
            print(f"\n🏝️ {destination_name} (ID: {destination_id})")
            
            if images_json:
                try:
                    images = json.loads(images_json)
                    print(f"   📸 Images: {len(images)}")
                    for i, image in enumerate(images):
                        print(f"   {i+1}. {image}")
                except:
                    print(f"   ❌ Invalid JSON: {images_json}")
            else:
                print("   📸 No images")
    
    finally:
        session.close()

def update_missing_image_records():
    """Update destinations that have no images in database."""
    
    print("\n🔄 Updating Missing Image Records...")
    print("=" * 50)
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Get destinations with no images
        stmt = text("""
            SELECT id, name 
            FROM destinations 
            WHERE images IS NULL OR images = '[]' OR images = ''
            ORDER BY id
        """)
        
        result = session.execute(stmt)
        destinations = result.fetchall()
        
        print(f"📍 Found {len(destinations)} destinations without images")
        
        for destination in destinations:
            destination_id, destination_name = destination
            
            # Create placeholder image URLs
            safe_name = destination_name.replace(" ", "_").replace(",", "").replace("'", "")
            placeholder_urls = [
                f"/static/images/placeholder-{safe_name}.jpg"
            ]
            
            # Update destination
            update_stmt = text("""
                UPDATE destinations 
                SET images = :image_urls 
                WHERE id = :destination_id
            """)
            
            session.execute(update_stmt, {
                "image_urls": json.dumps(placeholder_urls),
                "destination_id": destination_id
            })
            
            print(f"✅ Updated {destination_name} with placeholder")
        
        session.commit()
        print(f"\n🎉 Updated {len(destinations)} destinations with placeholders")
    
    finally:
        session.close()

def main():
    """Main function."""
    
    print("🖼️  Database Image Manager")
    print("=" * 50)
    
    choice = input("""
Choose an option:
1. Check current database images
2. Update missing image records with placeholders
3. Both (check then update)
4. Exit

Enter choice (1-4): """)
    
    if choice == "1":
        check_database_images()
    elif choice == "2":
        update_missing_image_records()
    elif choice == "3":
        check_database_images()
        update_missing_image_records()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
