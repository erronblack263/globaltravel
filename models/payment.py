from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(50), default="pending", index=True)
    stripe_payment_id = Column(String(255))
    stripe_charge_id = Column(String(255))
    
    # PayNow fields
    paynow_reference = Column(String(255))
    paynow_poll_url = Column(String(500))
    paynow_redirect_url = Column(String(500))
    paynow_transaction_id = Column(String(255))
    
    # EcoCash specific fields
    ecocash_transaction_id = Column(String(255))
    ecocash_reference = Column(String(255))
    customer_msisdn = Column(String(20))
    
    # PayPal fields
    paypal_order_id = Column(String(255))
    paypal_capture_id = Column(String(255))
    paypal_payer_id = Column(String(255))
    paypal_payer_email = Column(String(255))
    paypal_payment_status = Column(String(50))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="payments")
    user = relationship("User", back_populates="payments")
    tickets = relationship("Ticket", back_populates="payment", cascade="all, delete-orphan")