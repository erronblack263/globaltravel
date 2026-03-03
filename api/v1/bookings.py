from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import date, datetime

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.booking import Booking
from models.resort import Resort
from models.destination import Destination
from schemas.booking import (
    BookingCreate, BookingResponse, BookingUpdate, BookingSearch,
    BookingType, BookingStatus
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Create a new booking."""
    
    # Validate resort/destination exists and is available
    if booking_data.booking_type == BookingType.RESORT:
        stmt = select(Resort).where(
            and_(Resort.id == booking_data.resort_id, Resort.is_active == True)
        )
        result = await db.execute(stmt)
        resort = result.scalar_one_or_none()
        
        if not resort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resort not found"
            )
        
        if resort.available_rooms < booking_data.number_of_guests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough rooms available"
            )
    
    elif booking_data.booking_type == BookingType.DESTINATION:
        stmt = select(Destination).where(
            and_(Destination.id == booking_data.destination_id, Destination.is_active == True)
        )
        result = await db.execute(stmt)
        destination = result.scalar_one_or_none()
        
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination not found"
            )
    
    # Create booking
    db_booking = Booking(
        user_id=current_user.id,
        **booking_data.dict()
    )
    db.add(db_booking)
    
    # Update resort availability if applicable
    if booking_data.booking_type == BookingType.RESORT and resort:
        resort.available_rooms -= booking_data.number_of_guests
        db.add(resort)
    
    await db.commit()
    await db.refresh(db_booking)
    
    return db_booking


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    status: Optional[BookingStatus] = Query(None),
    booking_type: Optional[BookingType] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Booking]:
    """List current user's bookings with optional filtering."""
    
    query = select(Booking).where(Booking.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(Booking.status == status)
    if booking_type:
        query = query.where(Booking.booking_type == booking_type)
    if start_date:
        query = query.where(Booking.check_in_date >= start_date)
    if end_date:
        query = query.where(Booking.check_in_date <= end_date)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return list(bookings)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Get a specific booking."""
    
    try:
        stmt = select(Booking).where(
            and_(
                Booking.id == booking_id,
                Booking.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return booking
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving booking: {str(e)}"
        )


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Update booking (user's own bookings only)."""
    
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Cannot update if booking is already confirmed or completed
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update confirmed or completed booking"
        )
    
    # Update fields
    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    await db.commit()
    await db.refresh(booking)
    
    return booking


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Cancel booking (user's own bookings only)."""
    
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Cannot cancel if already cancelled or completed
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed booking"
        )
    
    # Update booking status
    booking.status = BookingStatus.CANCELLED
    
    # Restore resort availability if applicable
    if booking.booking_type == BookingType.RESORT:
        stmt = select(Resort).where(Resort.id == booking.resort_id)
        result = await db.execute(stmt)
        resort = result.scalar_one_or_none()
        if resort:
            resort.available_rooms += booking.number_of_guests
            db.add(resort)
    
    await db.commit()
    
    return {"message": "Booking cancelled successfully"}


@router.post("/search", response_model=List[BookingResponse])
async def search_bookings(
    search_params: BookingSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Booking]:
    """Advanced search for user's bookings."""
    
    query = select(Booking).where(Booking.user_id == current_user.id)
    
    # Apply search filters
    if search_params.status:
        query = query.where(Booking.status == search_params.status)
    if search_params.booking_type:
        query = query.where(Booking.booking_type == search_params.booking_type)
    if search_params.start_date:
        query = query.where(Booking.check_in_date >= search_params.start_date)
    if search_params.end_date:
        query = query.where(Booking.check_in_date <= search_params.end_date)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return list(bookings)
