"""
Manually update a specific destination with images.
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost/globaltravel"

def update_specific_destination():
    """Update a specific destination with custom images."""
    
    print("🔧 Manual Destination Image Update")
    print("=" * 50)
    
    destination_id = input("Enter destination ID: ")
    image_urls = input("Enter image URLs (comma-separated): ").split(",")
    
    # Clean up URLs
    image_urls = [url.strip() for url in image_urls if url.strip()]
    
    # Create sync engine and session
    sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", "+psycopg2"))
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        # Update destination
        stmt = text("""
            UPDATE destinations 
            SET images = :image_urls 
            WHERE id = :destination_id
        """)
        
        session.execute(stmt, {
            "image_urls": json.dumps(image_urls),
            "destination_id": destination_id
        })
        session.commit()
        
        print(f"✅ Updated destination {destination_id} with {len(image_urls)} images:")
        for i, url in enumerate(image_urls):
            print(f"   {i+1}. {url}")
    
    finally:
        session.close()

if __name__ == "__main__":
    update_specific_destination()
