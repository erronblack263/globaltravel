from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from decimal import Decimal


class PayPalPaymentRequest(BaseModel):
    """PayPal payment request schema."""
    booking_id: int = Field(..., description="Booking ID to link payment to")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    description: str = Field(default="Global Travel Booking", description="Payment description")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    cancel_url: Optional[str] = Field(None, description="Cancel URL if payment cancelled")


class PayPalOrderResponse(BaseModel):
    """PayPal order response schema."""
    order_id: str = Field(..., description="PayPal order ID")
    status: str = Field(..., description="Order status")
    approval_url: Optional[str] = Field(None, description="Approval URL for customer")
    create_time: str = Field(..., description="Order creation time")
    links: Dict[str, Any] = Field(default={}, description="Payment links")


class PayPalCaptureResponse(BaseModel):
    """PayPal capture response schema."""
    capture_id: str = Field(..., description="Capture ID")
    status: str = Field(..., description="Capture status")
    amount: Dict[str, Any] = Field(..., description="Captured amount")
    create_time: str = Field(..., description="Capture time")
    update_time: str = Field(..., description="Last update time")


class PayPalPaymentResponse(BaseModel):
    """PayPal payment response schema."""
    success: bool = Field(..., description="Payment success status")
    order_id: Optional[str] = Field(None, description="PayPal order ID")
    capture_id: Optional[str] = Field(None, description="PayPal capture ID")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    response: Optional[Dict[str, Any]] = Field(None, description="Full response data")
    message: str = Field(..., description="Response message")
    approval_url: Optional[str] = Field(None, description="Approval URL for customer")


class PayPalTestInfo(BaseModel):
    """PayPal test information schema."""
    environment: str = Field(..., description="Current environment")
    base_url: str = Field(..., description="API base URL")
    test_mode: bool = Field(..., description="Whether in test mode")
    test_accounts: Dict[str, str] = Field(..., description="Test account credentials")
    test_cards: list[Dict[str, str]] = Field(..., description="Test card information")


class PayPalWebhook(BaseModel):
    """PayPal webhook schema."""
    event_type: str = Field(..., description="Webhook event type")
    resource_type: str = Field(..., description="Resource type")
    event_version: str = Field(..., description="Event version")
    resource: Dict[str, Any] = Field(..., description="Event resource data")
    summary: str = Field(..., description="Event summary")
    create_time: str = Field(..., description="Event creation time")


class PayPalPaymentStatus(BaseModel):
    """PayPal payment status schema."""
    order_id: str = Field(..., description="PayPal order ID")
    status: str = Field(..., description="Payment status")
    intent: str = Field(..., description="Payment intent")
    purchase_units: list[Dict[str, Any]] = Field(..., description="Purchase units")
    payer: Optional[Dict[str, Any]] = Field(None, description="Payer information")
    create_time: str = Field(..., description="Creation time")
    update_time: str = Field(..., description="Last update time")
    links: Dict[str, Any] = Field(default={}, description="Related links")
