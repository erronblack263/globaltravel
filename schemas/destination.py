from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal


class DestinationBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., max_length=50)
    address: Optional[str] = None
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    entry_fee: Decimal = Field(default=0.00, ge=0)
    visiting_hours: Optional[str] = Field(None, max_length=100)
    best_time_to_visit: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    entry_fee: Optional[Decimal] = Field(None, ge=0)
    visiting_hours: Optional[str] = Field(None, max_length=100)
    best_time_to_visit: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class DestinationResponse(DestinationBase):
    id: int
    uuid: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DestinationSearch(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    max_entry_fee: Optional[Decimal] = Field(None, ge=0)