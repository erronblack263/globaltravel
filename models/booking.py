from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_type = Column(String(20), nullable=False)
    resort_id = Column(Integer, ForeignKey("resorts.id", ondelete="SET NULL"))
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="SET NULL"))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date)
    number_of_guests = Column(Integer, nullable=False, default=1)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending", index=True)
    special_requests = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    resort = relationship("Resort", back_populates="bookings")
    destination = relationship("Destination", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")
    
    # Constraint for booking type
    __table_args__ = (
        CheckConstraint(
            "(booking_type = 'resort' AND resort_id IS NOT NULL AND destination_id IS NULL) OR "
            "(booking_type = 'destination' AND destination_id IS NOT NULL AND resort_id IS NULL)",
            name='check_booking_type'
        ),
    )