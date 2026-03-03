from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from decimal import Decimal

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.destination import Destination
from schemas.destination import (
    DestinationCreate, DestinationResponse, DestinationUpdate, DestinationSearch
)
from schemas.destination_simple import DestinationSimple, DestinationDetail

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.post("/", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
async def create_destination(
    destination_data: DestinationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Destination:
    """Create a new destination (admin only)."""
    
    # TODO: Add admin role check
    
    db_destination = Destination(**destination_data.dict())
    db.add(db_destination)
    await db.commit()
    await db.refresh(db_destination)
    
    return db_destination




@router.get("/filter", response_model=List[DestinationSimple])
async def filter_destinations(
    name: Optional[str] = Query(None, description="Filter by destination name"),
    city: Optional[str] = Query(None, description="Filter by city name"),
    country: Optional[str] = Query(None, description="Filter by country name"),
    type: Optional[str] = Query(None, description="Filter by destination type (beach, mountain, cultural, etc)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Filter destinations by any combination of name, city, country, and type. JWT required."""
    
    # Build the base query
    query = select(Destination).where(Destination.is_active == True)
    
    # Add filters dynamically - all parameters work together with AND logic
    if name:
        query = query.where(Destination.name.ilike(f"%{name}%"))
    
    if city:
        query = query.where(Destination.city.ilike(f"%{city}%"))
    
    if country:
        query = query.where(Destination.country.ilike(f"%{country}%"))
    
    if type:
        query = query.where(Destination.type.ilike(f"%{type}%"))
    
    # Order by name for consistent results
    query = query.order_by(Destination.name)
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Filter error: {str(e)}"
        )


@router.get("/", response_model=List[DestinationSimple])
async def list_destinations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """List all destinations (JWT required)."""
    
    query = select(Destination).where(Destination.is_active == True)
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )




@router.get("/search", response_model=List[DestinationSimple])
async def search_by_name(
    name: str = Query(..., description="Search destinations by name"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Search destinations by name (matches name, city, country, type, description). JWT required."""
    
    # Simple name search across multiple fields
    query = select(Destination).where(
        and_(
            or_(
                Destination.name.ilike(f"%{name}%"),
                Destination.description.ilike(f"%{name}%"),
                Destination.city.ilike(f"%{name}%"),
                Destination.country.ilike(f"%{name}%"),
                Destination.type.ilike(f"%{name}%")
            ),
            Destination.is_active == True
        )
    )

    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/category/{category}", response_model=List[DestinationSimple])
async def get_destinations_by_category(
    category: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by category (beach, mountain, city, cultural, adventure)."""
    
    query = select(Destination).where(
        and_(
            Destination.type.ilike(f"%{category}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/country/{country}", response_model=List[DestinationSimple])
async def get_destinations_by_country(
    country: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by country."""
    
    query = select(Destination).where(
        and_(
            Destination.country.ilike(f"%{country}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/city/{city}", response_model=List[DestinationSimple])
async def get_destinations_by_city(
    city: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by city."""
    
    query = select(Destination).where(
        and_(
            Destination.city.ilike(f"%{city}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/address/{address}", response_model=List[DestinationSimple])
async def get_destinations_by_address(
    address: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by address."""
    
    query = select(Destination).where(
        and_(
            Destination.address.ilike(f"%{address}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/name/{name}", response_model=List[DestinationSimple])
async def get_destinations_by_name(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by exact name."""
    
    query = select(Destination).where(
        and_(
            Destination.name.ilike(f"%{name}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/description/{keyword}", response_model=List[DestinationSimple])
async def get_destinations_by_description(
    keyword: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by description keyword."""
    
    query = select(Destination).where(
        and_(
            Destination.description.ilike(f"%{keyword}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/visiting-hours/{hours}", response_model=List[DestinationSimple])
async def get_destinations_by_visiting_hours(
    hours: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by visiting hours."""
    
    query = select(Destination).where(
        and_(
            Destination.visiting_hours.ilike(f"%{hours}%"),
            Destination.is_active == True
        )
    )
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/entry-fee/{max_fee}", response_model=List[DestinationSimple])
async def get_destinations_by_entry_fee(
    max_fee: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Get destinations by maximum entry fee."""
    
    # Validate fee
    if max_fee < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry fee must be 0 or greater"
        )
    
    query = select(Destination).where(
        and_(
            Destination.entry_fee <= max_fee,
            Destination.is_active == True
        )
    ).order_by(Destination.entry_fee.asc())
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/{destination_id}", response_model=DestinationDetail)
async def get_destination(
    destination_id: int,
    db: AsyncSession = Depends(get_db)
) -> Destination:
    """Get destination by ID."""
    
    stmt = select(Destination).where(Destination.id == destination_id)
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    return destination


@router.get("/slug/{slug}", response_model=DestinationDetail)
async def get_destination_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get destination by slug (URL-friendly name)."""
    
    # Try to find destination by name or description containing the slug
    stmt = select(Destination).where(
        or_(
            Destination.name.ilike(f"%{slug.replace('-', ' ')}%"),
            Destination.name.ilike(f"%{slug.replace('%20', ' ')}%")
        )
    )
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    return destination




@router.get("/dest/{destination_id}", response_model=DestinationDetail)
async def get_destination_by_id(
    destination_id: int,
    db: AsyncSession = Depends(get_db)
) -> Destination:
    """Get destination by ID."""
    
    stmt = select(Destination).where(Destination.id == destination_id)
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    return destination


@router.put("/{destination_id}", response_model=DestinationResponse)
async def update_destination(
    destination_id: int,
    destination_update: DestinationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Destination:
    """Update destination (admin only)."""
    
    # TODO: Add admin role check
    
    stmt = select(Destination).where(Destination.id == destination_id)
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    # Update fields
    update_data = destination_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(destination, field, value)
    
    await db.commit()
    await db.refresh(destination)
    
    return destination


@router.delete("/{destination_id}")
async def delete_destination(
    destination_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Soft delete destination (admin only)."""
    
    # TODO: Add admin role check
    
    stmt = select(Destination).where(Destination.id == destination_id)
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    destination.is_active = False
    await db.commit()
    
    return {"message": "Destination deleted successfully"}


@router.post("/search", response_model=List[DestinationResponse])
async def search_destinations(
    search_params: DestinationSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[Destination]:
    """Advanced search for destinations."""
    
    query = select(Destination).where(Destination.is_active == True)
    
    # Apply search filters
    if search_params.city:
        query = query.where(Destination.city.ilike(f"%{search_params.city}%"))
    if search_params.country:
        query = query.where(Destination.country.ilike(f"%{search_params.country}%"))
    if search_params.type:
        query = query.where(Destination.type.ilike(f"%{search_params.type}%"))
    if search_params.max_entry_fee is not None:
        query = query.where(Destination.entry_fee <= search_params.max_entry_fee)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    try:
        result = await db.execute(query)
        destinations = result.scalars().all()
        
        return list(destinations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )
