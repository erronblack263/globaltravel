from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
import uuid
from decimal import Decimal
from enum import Enum


class BookingType(str, Enum):
    RESORT = "resort"
    DESTINATION = "destination"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingBase(BaseModel):
    booking_type: BookingType
    resort_id: Optional[int] = None
    destination_id: Optional[int] = None
    check_in_date: date
    check_out_date: Optional[date] = None
    number_of_guests: int = Field(default=1, gt=0)
    special_requests: Optional[str] = None
    
    @validator('check_out_date')
    def validate_check_out_date(cls, v, values):
        if v and 'check_in_date' in values:
            if v <= values['check_in_date']:
                raise ValueError('Check-out date must be after check-in date')
        return v
    
    @validator('destination_id')
    def validate_destination_booking(cls, v, values):
        if values.get('booking_type') == BookingType.DESTINATION and v is None:
            raise ValueError('Destination ID is required for destination bookings')
        if values.get('booking_type') == BookingType.RESORT and v is not None:
            raise ValueError('Destination ID should not be provided for resort bookings')
        return v
    
    @validator('resort_id')
    def validate_resort_booking(cls, v, values):
        if values.get('booking_type') == BookingType.RESORT and v is None:
            raise ValueError('Resort ID is required for resort bookings')
        if values.get('booking_type') == BookingType.DESTINATION and v is not None:
            raise ValueError('Resort ID should not be provided for destination bookings')
        return v


class BookingCreate(BookingBase):
    total_amount: Decimal = Field(..., gt=0)


class BookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    number_of_guests: Optional[int] = Field(None, gt=0)
    special_requests: Optional[str] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BookingBase):
    id: int
    uuid: uuid.UUID
    user_id: int
    total_amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingSearch(BaseModel):
    status: Optional[BookingStatus] = None
    booking_type: Optional[BookingType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None