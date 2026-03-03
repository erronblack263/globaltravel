from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, String
from typing import List, Optional
from decimal import Decimal

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.resort import Resort
from schemas.resort import (
    ResortCreate, ResortResponse, ResortUpdate, ResortSearch
)

router = APIRouter(prefix="/resorts", tags=["resorts"])


@router.post("/", response_model=ResortResponse, status_code=status.HTTP_201_CREATED)
async def create_resort(
    resort_data: ResortCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResortResponse:
    """Create a new resort (admin only)."""
    
    # TODO: Add admin role check
    
    db_resort = Resort(**resort_data.dict())
    db.add(db_resort)
    await db.commit()
    await db.refresh(db_resort)
    
    return db_resort


@router.get("/", response_model=List[ResortResponse])
async def list_resorts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """List all resorts (JWT required)."""
    
    query = select(Resort).where(Resort.is_active == True)
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/name/{name}", response_model=List[ResortResponse])
async def get_resorts_by_name(
    name: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by name."""
    
    query = select(Resort).where(
        and_(
            Resort.name.ilike(f"%{name}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/city/{city}", response_model=List[ResortResponse])
async def get_resorts_by_city(
    city: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by city."""
    
    query = select(Resort).where(
        and_(
            Resort.city.ilike(f"%{city}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/country/{country}", response_model=List[ResortResponse])
async def get_resorts_by_country(
    country: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by country."""
    
    query = select(Resort).where(
        and_(
            Resort.country.ilike(f"%{country}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/rating/{star_rating}", response_model=List[ResortResponse])
async def get_resorts_by_star_rating(
    star_rating: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by star rating."""
    
    # Validate star rating
    if star_rating < 1 or star_rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Star rating must be between 1 and 5"
        )
    
    query = select(Resort).where(
        and_(
            Resort.star_rating == star_rating,
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/price/{max_price}", response_model=List[ResortResponse])
async def get_resorts_by_price(
    max_price: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by maximum price per night."""
    
    # Validate price
    if max_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )
    
    query = select(Resort).where(
        and_(
            Resort.price_per_night <= max_price,
            Resort.is_active == True
        )
    ).order_by(Resort.price_per_night.asc())
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/rooms/{min_rooms}", response_model=List[ResortResponse])
async def get_resorts_by_total_rooms(
    min_rooms: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by minimum total rooms."""
    
    # Validate room count
    if min_rooms <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room count must be greater than 0"
        )
    
    query = select(Resort).where(
        and_(
            Resort.total_rooms >= min_rooms,
            Resort.is_active == True
        )
    ).order_by(Resort.total_rooms.desc())
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/available/{min_rooms}", response_model=List[ResortResponse])
async def get_resorts_by_available_rooms(
    min_rooms: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by minimum available rooms."""
    
    # Validate room count
    if min_rooms <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room count must be greater than 0"
        )
    
    query = select(Resort).where(
        and_(
            Resort.available_rooms >= min_rooms,
            Resort.is_active == True
        )
    ).order_by(Resort.available_rooms.desc())
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/description/{keyword}", response_model=List[ResortResponse])
async def get_resorts_by_description(
    keyword: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by description keyword."""
    
    query = select(Resort).where(
        and_(
            Resort.description.ilike(f"%{keyword}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/address/{address}", response_model=List[ResortResponse])
async def get_resorts_by_address(
    address: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by address."""
    
    query = select(Resort).where(
        and_(
            Resort.address.ilike(f"%{address}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/amenities/{amenity}", response_model=List[ResortResponse])
async def get_resorts_by_amenity(
    amenity: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by amenity."""
    
    # For JSON arrays, use cast to string and ilike for searching
    query = select(Resort).where(
        and_(
            Resort.amenities.cast(String).ilike(f"%{amenity}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/status/{status}", response_model=List[ResortResponse])
async def get_resorts_by_status(
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by status (active/inactive)."""
    
    # Validate status
    if status.lower() not in ['active', 'inactive']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'active' or 'inactive'"
        )
    
    is_active = status.lower() == 'active'
    
    query = select(Resort).where(Resort.is_active == is_active)
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/images/{keyword}", response_model=List[ResortResponse])
async def get_resorts_by_image_keyword(
    keyword: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by image URL keyword."""
    
    # For JSON arrays, we need to use a different approach
    # This will search for resorts where any image contains the keyword
    query = select(Resort).where(
        and_(
            Resort.images.cast(String).ilike(f"%{keyword}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/image-url/{url:path}", response_model=List[ResortResponse])
async def get_resorts_by_image_url(
    url: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Get resorts by exact image URL."""
    
    # Debug: print the URL we're searching for
    print(f"Searching for URL: {url}")
    
    query = select(Resort).where(
        and_(
            Resort.images.cast(String).ilike(f"%{url}%"),
            Resort.is_active == True
        )
    )
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    print(f"Found {len(resorts)} resorts")
    
    return list(resorts)


@router.get("/{resort_id}", response_model=ResortResponse)
async def get_resort(
    resort_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResortResponse:
    """Get resort by ID."""
    
    stmt = select(Resort).where(
        and_(Resort.id == resort_id, Resort.is_active == True)
    )
    result = await db.execute(stmt)
    resort = result.scalar_one_or_none()
    
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort not found"
        )
    
    return resort


@router.put("/{resort_id}", response_model=ResortResponse)
async def update_resort(
    resort_id: int,
    resort_update: ResortUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ResortResponse:
    """Update resort (admin only)."""
    
    # TODO: Add admin role check
    
    stmt = select(Resort).where(Resort.id == resort_id)
    result = await db.execute(stmt)
    resort = result.scalar_one_or_none()
    
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort not found"
        )
    
    # Update fields
    update_data = resort_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resort, field, value)
    
    await db.commit()
    await db.refresh(resort)
    
    return resort


@router.delete("/{resort_id}")
async def delete_resort(
    resort_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Soft delete resort (admin only)."""
    
    # TODO: Add admin role check
    
    stmt = select(Resort).where(Resort.id == resort_id)
    result = await db.execute(stmt)
    resort = result.scalar_one_or_none()
    
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort not found"
        )
    
    resort.is_active = False
    await db.commit()
    
    return {"message": "Resort deleted successfully"}


@router.post("/search", response_model=List[ResortResponse])
async def search_resorts(
    search_params: ResortSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[ResortResponse]:
    """Advanced search for resorts."""
    
    query = select(Resort).where(Resort.is_active == True)
    
    # Apply search filters
    if search_params.city:
        query = query.where(Resort.city.ilike(f"%{search_params.city}%"))
    if search_params.country:
        query = query.where(Resort.country.ilike(f"%{search_params.country}%"))
    if search_params.type:
        query = query.where(Resort.type.ilike(f"%{search_params.type}%"))
    if search_params.min_price is not None:
        query = query.where(Resort.price_per_night >= search_params.min_price)
    if search_params.max_price is not None:
        query = query.where(Resort.price_per_night <= search_params.max_price)
    if search_params.min_star_rating is not None:
        query = query.where(Resort.star_rating >= search_params.min_star_rating)
    if search_params.available_rooms is not None:
        query = query.where(Resort.available_rooms >= search_params.available_rooms)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)
