from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class DestinationSimple(BaseModel):
    """Simple destination response for public API."""
    id: int
    name: str
    type: str
    city: str
    country: str
    entry_fee: Decimal
    images: List[str]
    
    class Config:
        from_attributes = True


class DestinationDetail(BaseModel):
    """Detailed destination response when needed."""
    id: int
    name: str
    description: str
    type: str
    address: str
    city: str
    country: str
    latitude: Decimal
    longitude: Decimal
    entry_fee: Decimal
    visiting_hours: str
    best_time_to_visit: str
    images: List[str]
    
    class Config:
        from_attributes = True
