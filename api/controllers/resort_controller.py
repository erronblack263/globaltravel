from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from decimal import Decimal

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.resort import Resort
from schemas.resort import (
    ResortCreate, ResortResponse, ResortUpdate, ResortSearch
)

router = APIRouter()


@router.post("/", response_model=ResortResponse, status_code=status.HTTP_201_CREATED)
async def create_resort(
    resort_data: ResortCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Resort:
    """Create a new resort (admin only)."""
    
    # TODO: Add admin role check
    
    db_resort = Resort(**resort_data.dict())
    db.add(db_resort)
    await db.commit()
    await db.refresh(db_resort)
    
    return db_resort


@router.get("/", response_model=List[ResortResponse])
async def list_resorts(
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    resort_type: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    min_star_rating: Optional[int] = Query(None, ge=1, le=5),
    available_rooms: Optional[int] = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[Resort]:
    """List resorts with optional filtering."""
    
    query = select(Resort).where(Resort.is_active == True)
    
    # Apply filters
    if city:
        query = query.where(Resort.city.ilike(f"%{city}%"))
    if country:
        query = query.where(Resort.country.ilike(f"%{country}%"))
    if resort_type:
        query = query.where(Resort.type.ilike(f"%{resort_type}%"))
    if min_price is not None:
        query = query.where(Resort.price_per_night >= min_price)
    if max_price is not None:
        query = query.where(Resort.price_per_night <= max_price)
    if min_star_rating is not None:
        query = query.where(Resort.star_rating >= min_star_rating)
    if available_rooms is not None:
        query = query.where(Resort.available_rooms >= available_rooms)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    resorts = result.scalars().all()
    
    return list(resorts)


@router.get("/{resort_id}", response_model=ResortResponse)
async def get_resort(
    resort_id: int,
    db: AsyncSession = Depends(get_db)
) -> Resort:
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
) -> Resort:
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
) -> List[Resort]:
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
