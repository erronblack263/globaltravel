from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class EcocashPaymentRequest(BaseModel):
    """Ecocash payment request schema."""
    booking_id: int = Field(..., description="Booking ID to link payment to")
    customer_msisdn: str = Field(
        ..., 
        description="Customer phone number. Accepts formats: 0774222475, 263774222475, +263774222475",
        examples=["0774222475", "263774222475", "+263774222475"]
    )
    amount: float = Field(..., gt=0, description="Payment amount")
    reason: str = Field(default="Global Travel Booking", description="Payment description")
    currency: str = Field(default="USD", description="Currency code")

class EcocashPaymentResponse(BaseModel):
    """Ecocash payment response schema."""
    status_code: int
    response: Dict[str, Any]
    source_reference: str
    success: bool
    message: str
    test_pins: Optional[list] = None

class EcocashPaymentStatus(BaseModel):
    """Ecocash payment status schema."""
    status: str
    source_reference: str
    message: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None

class EcocashWebhook(BaseModel):
    """Ecocash webhook schema."""
    transaction_id: str
    status: str
    amount: float
    currency: str
    merchant_id: str
    timestamp: datetime
    signature: Optional[str] = None

class EcocashTestInfo(BaseModel):
    """Ecocash test information schema."""
    environment: str
    test_pins: list
    merchant_code: str
    api_key_prefix: str
