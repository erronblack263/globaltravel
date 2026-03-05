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
from models.destination import Destination
from schemas.booking_separate import (
    DestinationBookingCreate, DestinationBookingResponse, DestinationBookingUpdate,
    BookingStatus
)

router = APIRouter(prefix="/destination-bookings", tags=["destination-bookings"])


@router.post("/", response_model=DestinationBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_destination_booking(
    booking_data: DestinationBookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Create a new destination booking."""
    
    # Validate destination exists and is active
    stmt = select(Destination).where(
        and_(Destination.id == booking_data.destination_id, Destination.is_active == True)
    )
    result = await db.execute(stmt)
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found or not available"
        )
    
    # Calculate total amount (destination entry fee * number of guests)
    total_amount = destination.entry_fee * booking_data.number_of_guests
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        booking_type="destination",
        destination_id=booking_data.destination_id,
        resort_id=None,  # No resort for destination bookings
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,  # Optional for day trips
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


@router.get("/", response_model=List[DestinationBookingResponse])
async def get_destination_bookings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Booking]:
    """Get all destination bookings for current user."""
    
    try:
        query = select(Booking, Destination).join(
            Destination, Booking.destination_id == Destination.id
        ).where(
            and_(
                Booking.user_id == current_user.id,
                Booking.destination_id.is_not(None),
                Booking.resort_id.is_(None)  # Only destination bookings (no resort)
            )
        ).order_by(Booking.created_at.desc())
        
        result = await db.execute(query)
        bookings_with_destinations = result.all()
        
        # Convert to response format with destination details
        bookings = []
        for booking, destination in bookings_with_destinations:
            booking.uuid = str(booking.uuid)
            # Add destination details to booking
            booking.destination_name = destination.name
            booking.destination_city = destination.city
            booking.destination_country = destination.country
            bookings.append(booking)
        
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving destination bookings: {str(e)}"
        )


@router.get("/{booking_id}", response_model=DestinationBookingResponse)
async def get_destination_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Get a specific destination booking."""
    
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.destination_id.is_not(None),
            Booking.resort_id.is_(None)  # Only destination bookings
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination booking not found"
        )
    
    # Convert UUID to string for response
    booking.uuid = str(booking.uuid)
    
    return booking


@router.put("/{booking_id}", response_model=DestinationBookingResponse)
async def update_destination_booking(
    booking_id: int,
    booking_update: DestinationBookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Booking:
    """Update a destination booking."""
    
    # Get existing booking
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.destination_id.is_not(None),
            Booking.resort_id.is_(None)  # Only destination bookings
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination booking not found"
        )
    
    # Update booking fields
    update_data = booking_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    # Recalculate total amount if guests changed
    if 'number_of_guests' in update_data:
        # Get destination info
        dest_stmt = select(Destination).where(Destination.id == booking.destination_id)
        dest_result = await db.execute(dest_stmt)
        destination = dest_result.scalar_one_or_none()
        
        if destination:
            booking.total_amount = destination.entry_fee * booking.number_of_guests
    
    await db.commit()
    await db.refresh(booking)
    
    # Convert UUID to string for response
    booking.uuid = str(booking.uuid)
    
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_destination_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a destination booking."""
    
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
            Booking.destination_id.is_not(None),
            Booking.resort_id.is_(None)  # Only destination bookings
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination booking not found"
        )
    
    # Only allow deletion of pending bookings
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete confirmed or completed bookings"
        )
    
    await db.delete(booking)
    await db.commit()
