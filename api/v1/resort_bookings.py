from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.booking import Booking
from models.resort import Resort
from schemas.booking_separate import (
    ResortBookingCreate, ResortBookingResponse, ResortBookingUpdate,
    BookingStatus
)

router = APIRouter(prefix="/resort-bookings", tags=["resort-bookings"])


@router.post("/", response_model=ResortBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_resort_booking(
    booking_data: ResortBookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Create a new resort booking."""
    
    # Validate resort exists and is available
    stmt = select(Resort).where(
        and_(Resort.id == booking_data.resort_id, Resort.is_active == True)
    )
    result = await db.execute(stmt)
    resort = result.scalar_one_or_none()
    
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort not found or not available"
        )
    
    if resort.available_rooms < booking_data.number_of_guests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough rooms available"
        )
    
    # Calculate total amount (resort price per night * number of nights)
    nights = (booking_data.check_out_date - booking_data.check_in_date).days
    total_amount = resort.price_per_night * nights * booking_data.number_of_guests
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        booking_type="resort",
        resort_id=booking_data.resort_id,
        destination_id=None,  # Resort bookings don't need destination_id
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        number_of_guests=booking_data.number_of_guests,
        special_requests=booking_data.special_requests,
        total_amount=total_amount,
        status=BookingStatus.PENDING
    )
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    # Convert UUID to string for response
    booking.uuid = str(booking.uuid)
    
    return booking


@router.get("/", response_model=List[ResortBookingResponse])
async def get_resort_bookings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
) -> List[Booking]:
    """Get current user's resort bookings."""
    
    try:
        query = select(Booking).where(
            and_(
                Booking.user_id == current_user.id,
                Booking.resort_id.is_not(None),
                Booking.destination_id.is_(None)  # Only resort bookings (no destination)
            )
        )
        
        if status_filter:
            query = query.where(Booking.status == status_filter)
        
        query = query.offset(skip).limit(limit).order_by(Booking.created_at.desc())
        
        result = await db.execute(query)
        bookings = result.scalars().all()
        
        # Convert UUID to string for each booking
        for booking in bookings:
            booking.uuid = str(booking.uuid)
        
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resort bookings: {str(e)}"
        )


@router.get("/{booking_id}", response_model=ResortBookingResponse)
async def get_resort_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Get a specific resort booking."""
    
    try:
        stmt = select(Booking).where(
            and_(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
                Booking.resort_id.is_not(None),
                Booking.destination_id.is_(None)  # Only resort bookings (no destination)
            )
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resort booking not found"
            )
        
        # Convert UUID to string for response
        booking.uuid = str(booking.uuid)
        
        return booking
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resort booking: {str(e)}"
        )


@router.put("/{booking_id}", response_model=ResortBookingResponse)
async def update_resort_booking(
    booking_id: int,
    booking_update: ResortBookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Update a resort booking."""
    
    # Get existing booking
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.resort_id.is_not(None),
            Booking.destination_id.is_(None)  # Only resort bookings (no destination)
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort booking not found"
        )
    
    # Update booking fields
    update_data = booking_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    # Recalculate total amount if dates or guests changed
    if 'check_in_date' in update_data or 'check_out_date' in update_data or 'number_of_guests' in update_data:
        # Get resort info
        resort_stmt = select(Resort).where(Resort.id == booking.resort_id)
        resort_result = await db.execute(resort_stmt)
        resort = resort_result.scalar_one_or_none()
        
        if resort:
            nights = (booking.check_out_date - booking.check_in_date).days
            booking.total_amount = resort.price_per_night * nights * booking.number_of_guests
    
    await db.commit()
    await db.refresh(booking)
    
    # Convert UUID to string for response
    booking.uuid = str(booking.uuid)
    
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resort_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a resort booking."""
    
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.resort_id.is_not(None),
            Booking.destination_id.is_(None)  # Only resort bookings (no destination)
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resort booking not found"
        )
    
    # Only allow deletion of pending bookings
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete confirmed or completed bookings"
        )
    
    await db.delete(booking)
    await db.commit()
