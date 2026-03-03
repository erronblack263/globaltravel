from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    qr_code = Column(Text)
    pdf_url = Column(Text)
    status = Column(String(50), default="active", index=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    payment = relationship("Payment", back_populates="tickets")