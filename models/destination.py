from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Destination(Base):
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False, index=True)
    address = Column(Text)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    entry_fee = Column(Numeric(10, 2), default=0.00)
    visiting_hours = Column(String(100))
    best_time_to_visit = Column(String(100))
    images = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="destination")