from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import csv
import io

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.destination import Destination
from schemas.destination_simple import DestinationSimple

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/import-destinations", response_model=dict)
async def import_destinations_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Import destinations from CSV file (admin only)."""
    
    # TODO: Add admin role check
    
    # Check if file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Get existing destinations to avoid duplicates
    stmt = select(Destination)
    result = await db.execute(stmt)
    existing_destinations = result.scalars().all()
    existing_names = {dest.name for dest in existing_destinations}
    
    # Read CSV content
    content = await file.read()
    csv_content = content.decode('utf-8')
    
    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    new_destinations = []
    errors = []
    
    for row_num, row in enumerate(csv_reader, 1):
        try:
            # Skip if destination already exists
            if row['name'] in existing_names:
                continue
            
            # Validate required fields
            if not all(key in row for key in ['name', 'type', 'city', 'country']):
                errors.append(f"Row {row_num}: Missing required fields")
                continue
            
            # Parse images (comma-separated)
            images = [img.strip() for img in row.get('images', '').split(',') if img.strip()]
            
            # Create destination object
            destination = Destination(
                name=row['name'],
                description=row.get('description', ''),
                type=row['type'],
                address=f"{row['city']}, {row['country']}",
                city=row['city'],
                country=row['country'],
                latitude=float(row.get('latitude', 0)),
                longitude=float(row.get('longitude', 0)),
                entry_fee=float(row.get('entry_fee', 0)),
                visiting_hours=row.get('visiting_hours', '24/7'),
                best_time_to_visit=row.get('best_time_to_visit', 'Year-round'),
                images=images,
                is_active=True
            )
            
            new_destinations.append(destination)
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    # Add new destinations to database
    if new_destinations:
        for destination in new_destinations:
            db.add(destination)
        
        await db.commit()
    
    return {
        "message": f"Successfully imported {len(new_destinations)} new destinations",
        "total_destinations": len(existing_destinations) + len(new_destinations),
        "skipped": len(existing_names),
        "errors": errors
    }

@router.get("/stats", response_model=dict)
async def get_admin_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get database statistics (admin only)."""
    
    # TODO: Add admin role check
    
    # Count destinations by type
    stmt = select(Destination).where(Destination.is_active == True)
    result = await db.execute(stmt)
    all_destinations = result.scalars().all()
    
    type_counts = {}
    for dest in all_destinations:
        type_counts[dest.type] = type_counts.get(dest.type, 0) + 1
    
    return {
        "total_destinations": len(all_destinations),
        "destinations_by_type": type_counts,
        "last_updated": "2024-01-01T00:00:00Z"
    }
