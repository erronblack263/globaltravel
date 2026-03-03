from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketBase(BaseModel):
    """Base ticket schema."""
    ticket_number: str
    qr_code_url: str
    pdf_url: str
    status: str
    issued_date: datetime
    valid_until: datetime

class TicketCreate(BaseModel):
    """Schema for creating a ticket."""
    booking_id: int
    payment_id: Optional[int] = None

class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    status: Optional[str] = None
    valid_until: Optional[datetime] = None

class TicketResponse(TicketBase):
    """Ticket response schema."""
    id: int
    booking_id: int
    user_id: int
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TicketValidation(BaseModel):
    """Ticket validation response."""
    ticket_id: int
    is_valid: bool
    status: str
    issued_date: datetime
    valid_until: datetime
