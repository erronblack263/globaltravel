from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# Resort Booking Schemas
class ResortBookingBase(BaseModel):
    resort_id: int = Field(..., description="ID of the resort to book")
    check_in_date: date = Field(..., description="Check-in date")
    check_out_date: date = Field(..., description="Check-out date")
    number_of_guests: int = Field(default=1, gt=0, description="Number of guests")
    special_requests: Optional[str] = Field(None, description="Special requests for the booking")
    
    @validator('check_out_date')
    def check_out_date_must_be_after_check_in(cls, v, values):
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('check_out_date must be after check_in_date')
        return v
    
    @validator('check_in_date')
    def check_in_date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError('check_in_date must be in the future')
        return v


class ResortBookingCreate(ResortBookingBase):
    pass


class ResortBookingResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    resort_id: int
    check_in_date: date
    check_out_date: date
    number_of_guests: int
    special_requests: Optional[str] = None
    total_amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResortBookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    number_of_guests: Optional[int] = Field(None, gt=0)
    special_requests: Optional[str] = None
    status: Optional[BookingStatus] = None


# Destination Booking Schemas
class DestinationBookingBase(BaseModel):
    destination_id: int = Field(..., description="ID of the destination to book")
    check_in_date: date = Field(..., description="Visit date")
    check_out_date: Optional[date] = Field(None, description="End date (optional for day trips)")
    number_of_guests: int = Field(default=1, gt=0, description="Number of guests")
    special_requests: Optional[str] = Field(None, description="Special requests for the booking")
    
    @validator('check_out_date')
    def check_out_date_must_be_after_check_in(cls, v, values):
        if v is not None and 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('check_out_date must be after check_in_date')
        return v
    
    @validator('check_in_date')
    def check_in_date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError('check_in_date must be in the future')
        return v


class DestinationBookingCreate(DestinationBookingBase):
    pass


class DestinationBookingResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    destination_id: int
    check_in_date: date
    check_out_date: Optional[date] = None
    number_of_guests: int
    special_requests: Optional[str] = None
    total_amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DestinationBookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None  # Can be None for day trips
    number_of_guests: Optional[int] = Field(None, gt=0)
    special_requests: Optional[str] = None
    status: Optional[BookingStatus] = None


# Combined Booking List Response
class BookingListResponse(BaseModel):
    resort_bookings: list[ResortBookingResponse] = []
    destination_bookings: list[DestinationBookingResponse] = []
