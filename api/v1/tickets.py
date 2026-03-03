from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.ticket import Ticket
from models.booking import Booking
from schemas.ticket import TicketResponse, TicketCreate
import services.ticket_service as ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Ticket:
    """Create a new ticket for a booking."""
    
    # Verify booking exists and belongs to user
    stmt = select(Booking).where(
        and_(
            Booking.id == ticket_data.booking_id,
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
    
    # Create ticket
    ticket = await ticket_service.create_ticket(
        db=db,
        booking_id=booking.id,
        user_id=current_user.id,
        payment_id=ticket_data.payment_id
    )
    
    return ticket

@router.get("/", response_model=List[TicketResponse])
async def get_user_tickets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Ticket]:
    """Get all tickets for the current user."""
    
    stmt = select(Ticket).where(Ticket.user_id == current_user.id)
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    
    return list(tickets)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Ticket:
    """Get a specific ticket by ID."""
    
    stmt = select(Ticket).where(
        and_(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return ticket

@router.get("/booking/{booking_id}", response_model=List[TicketResponse])
async def get_tickets_by_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Ticket]:
    """Get all tickets for a specific booking."""
    
    # Verify booking belongs to user
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
    
    # Get tickets for this booking
    stmt = select(Ticket).where(Ticket.booking_id == booking_id)
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    
    return list(tickets)

@router.post("/{ticket_id}/validate", response_model=dict)
async def validate_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Validate a ticket (check if it's still valid)."""
    
    stmt = select(Ticket).where(
        and_(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    is_valid = await ticket_service.validate_ticket(db, ticket_id)
    
    return {
        "ticket_id": ticket_id,
        "is_valid": is_valid,
        "status": ticket.status,
        "issued_date": ticket.issued_date,
        "valid_until": ticket.valid_until
    }

@router.get("/{ticket_id}/qr", response_model=dict)
async def get_ticket_qr(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get QR code for a ticket."""
    
    stmt = select(Ticket).where(
        and_(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return {
        "ticket_id": ticket_id,
        "ticket_number": ticket.ticket_number,
        "qr_code_url": ticket.qr_code_url,
        "pdf_url": ticket.pdf_url
    }
