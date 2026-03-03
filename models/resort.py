from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Resort(Base):
    __tablename__ = "resorts"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    star_rating = Column(Integer, CheckConstraint('star_rating >= 1 AND star_rating <= 5'))
    price_per_night = Column(Numeric(10, 2), nullable=False)
    total_rooms = Column(Integer, nullable=False)
    available_rooms = Column(Integer, nullable=False)
    amenities = Column(JSONB)
    images = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="resort")