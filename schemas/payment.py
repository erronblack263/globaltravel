from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethod


class PaymentCreate(PaymentBase):
    booking_id: int


class PaymentUpdate(BaseModel):
    payment_status: Optional[PaymentStatus] = None
    stripe_payment_id: Optional[str] = Field(None, max_length=255)
    stripe_charge_id: Optional[str] = Field(None, max_length=255)


class PaymentResponse(PaymentBase):
    id: int
    uuid: uuid.UUID
    booking_id: int
    user_id: int
    payment_status: PaymentStatus
    stripe_payment_id: Optional[str]
    stripe_charge_id: Optional[str]
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StripePaymentIntent(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: Decimal
    currency: str


class PaymentConfirmation(BaseModel):
    payment_intent_id: str