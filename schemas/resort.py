from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal


class ResortBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., max_length=50)
    address: str
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    price_per_night: Decimal = Field(..., gt=0)
    total_rooms: int = Field(..., gt=0)
    available_rooms: int = Field(..., ge=0)
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None


class ResortCreate(ResortBase):
    pass


class ResortUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    price_per_night: Optional[Decimal] = Field(None, ge=0)
    total_rooms: Optional[int] = Field(None, gt=0)
    available_rooms: Optional[int] = Field(None, ge=0)
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ResortResponse(ResortBase):
    id: int
    uuid: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResortSearch(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    min_star_rating: Optional[int] = Field(None, ge=1, le=5)
    available_rooms: Optional[int] = Field(None, gt=0)