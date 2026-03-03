from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date, timedelta
from typing import List, Optional
from decimal import Decimal

from models.booking import Booking
from models.resort import Resort
from models.destination import Destination
from schemas.booking import BookingCreate, BookingType, BookingStatus


class BookingService:
    """Service for booking-related business logic."""
    
    @staticmethod
    async def calculate_resort_price(
        resort_id: int,
        check_in_date: date,
        check_out_date: date,
        number_of_guests: int,
        db: AsyncSession
    ) -> Decimal:
        """Calculate total price for resort booking."""
        
        stmt = select(Resort).where(Resort.id == resort_id)
        result = await db.execute(stmt)
        resort = result.scalar_one_or_none()
        
        if not resort:
            raise ValueError("Resort not found")
        
        # Calculate number of nights
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            raise ValueError("Check-out date must be after check-in date")
        
        # Calculate base price
        total_price = resort.price_per_night * nights * number_of_guests
        
        return total_price
    
    @staticmethod
    async def calculate_destination_price(
        destination_id: int,
        number_of_guests: int,
        db: AsyncSession
    ) -> Decimal:
        """Calculate total price for destination booking."""
        
        stmt = select(Destination).where(Destination.id == destination_id)
        result = await db.execute(stmt)
        destination = result.scalar_one_or_none()
        
        if not destination:
            raise ValueError("Destination not found")
        
        # Destination pricing is usually per person
        total_price = destination.entry_fee * number_of_guests
        
        return total_price
    
    @staticmethod
    async def check_resort_availability(
        resort_id: int,
        check_in_date: date,
        check_out_date: date,
        number_of_guests: int,
        db: AsyncSession
    ) -> bool:
        """Check if resort is available for the given dates."""
        
        # Get resort info
        stmt = select(Resort).where(Resort.id == resort_id)
        result = await db.execute(stmt)
        resort = result.scalar_one_or_none()
        
        if not resort or not resort.is_active:
            return False
        
        if resort.available_rooms < number_of_guests:
            return False
        
        # Check for overlapping bookings
        stmt = select(Booking).where(
            and_(
                Booking.resort_id == resort_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    and_(
                        Booking.check_in_date <= check_in_date,
                        Booking.check_out_date >= check_in_date
                    ),
                    and_(
                        Booking.check_in_date <= check_out_date,
                        Booking.check_out_date >= check_out_date
                    ),
                    and_(
                        Booking.check_in_date >= check_in_date,
                        Booking.check_out_date <= check_out_date
                    )
                )
            )
        )
        result = await db.execute(stmt)
        overlapping_bookings = result.scalars().all()
        
        # Calculate total guests from overlapping bookings
        total_overlapping_guests = sum(
            booking.number_of_guests for booking in overlapping_bookings
        )
        
        # Check if available
        available_rooms = resort.total_rooms - total_overlapping_guests
        return available_rooms >= number_of_guests
    
    @staticmethod
    async def get_user_booking_stats(
        user_id: int,
        db: AsyncSession
    ) -> dict:
        """Get booking statistics for a user."""
        
        # Total bookings
        total_stmt = select(func.count(Booking.id)).where(Booking.user_id == user_id)
        total_result = await db.execute(total_stmt)
        total_bookings = total_result.scalar() or 0
        
        # Bookings by status
        status_stats = {}
        for status in BookingStatus:
            status_stmt = select(func.count(Booking.id)).where(
                and_(Booking.user_id == user_id, Booking.status == status)
            )
            status_result = await db.execute(status_stmt)
            status_stats[status.value] = status_result.scalar() or 0
        
        # Total amount spent
        amount_stmt = select(func.sum(Booking.total_amount)).where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.COMPLETED
            )
        )
        amount_result = await db.execute(amount_stmt)
        total_spent = amount_result.scalar() or Decimal('0')
        
        # Recent bookings (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_stmt = select(func.count(Booking.id)).where(
            and_(
                Booking.user_id == user_id,
                Booking.created_at >= thirty_days_ago
            )
        )
        recent_result = await db.execute(recent_stmt)
        recent_bookings = recent_result.scalar() or 0
        
        return {
            "total_bookings": total_bookings,
            "status_breakdown": status_stats,
            "total_spent": float(total_spent),
            "recent_bookings": recent_bookings
        }
    
    @staticmethod
    async def get_popular_destinations(
        db: AsyncSession,
        limit: int = 10
    ) -> List[dict]:
        """Get popular destinations based on booking count."""
        
        stmt = select(
            Destination.id,
            Destination.name,
            Destination.city,
            Destination.country,
            func.count(Booking.id).label('booking_count')
        ).join(
            Booking, Destination.id == Booking.destination_id
        ).where(
            and_(
                Destination.is_active == True,
                Booking.status == BookingStatus.COMPLETED
            )
        ).group_by(
            Destination.id, Destination.name, Destination.city, Destination.country
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        destinations = result.all()
        
        return [
            {
                "id": dest.id,
                "name": dest.name,
                "city": dest.city,
                "country": dest.country,
                "booking_count": dest.booking_count
            }
            for dest in destinations
        ]
    
    @staticmethod
    async def get_popular_resorts(
        db: AsyncSession,
        limit: int = 10
    ) -> List[dict]:
        """Get popular resorts based on booking count."""
        
        stmt = select(
            Resort.id,
            Resort.name,
            Resort.city,
            Resort.country,
            Resort.star_rating,
            func.count(Booking.id).label('booking_count')
        ).join(
            Booking, Resort.id == Booking.resort_id
        ).where(
            and_(
                Resort.is_active == True,
                Booking.status == BookingStatus.COMPLETED
            )
        ).group_by(
            Resort.id, Resort.name, Resort.city, Resort.country, Resort.star_rating
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        resorts = result.all()
        
        return [
            {
                "id": resort.id,
                "name": resort.name,
                "city": resort.city,
                "country": resort.country,
                "star_rating": resort.star_rating,
                "booking_count": resort.booking_count
            }
            for resort in resorts
        ]
