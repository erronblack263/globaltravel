from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from decimal import Decimal

import stripe

from core.database import get_db
from core.config import settings
from core.dependancies import get_current_active_user
from models.user import User
from models.payment import Payment
from models.booking import Booking
from schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentUpdate,
    StripePaymentIntent, PaymentConfirmation,
    PaymentMethod, PaymentStatus, PayNowPaymentResponse
)
from schemas.ecocash import (
    EcocashPaymentRequest, EcocashPaymentResponse,
    EcocashPaymentStatus, EcocashTestInfo
)
from services.ecocash_service import ecocash_service
from services.paynow_service import paynow_service

# PayPal imports
from schemas.paypal import (
    PayPalPaymentRequest, PayPalPaymentResponse,
    PayPalTestInfo, PayPalWebhook
)
from services.paypal_service import paypal_service

router = APIRouter(prefix="/payments", tags=["payments"])

# Configure Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-payment-intent", response_model=StripePaymentIntent)
async def create_payment_intent(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> StripePaymentIntent:
    """Create a Stripe payment intent for a booking."""
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not available"
        )
    
    # Verify booking exists and belongs to user
    stmt = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if payment already exists
    stmt = select(Payment).where(
        and_(
            Payment.booking_id == booking_id,
            Payment.payment_status == PaymentStatus.COMPLETED
        )
    )
    result = await db.execute(stmt)
    existing_payment = result.scalar_one_or_none()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already completed for this booking"
        )
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(booking.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'booking_id': booking_id,
                'user_id': current_user.id
            }
        )
        
        return StripePaymentIntent(
            payment_intent_id=intent.id,
            client_secret=intent.client_secret,
            amount=booking.total_amount,
            currency='usd'
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )


@router.post("/confirm-payment", response_model=PaymentResponse)
async def confirm_payment(
    payment_confirmation: PaymentConfirmation,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Payment:
    """Confirm payment and create payment record."""
    
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not available"
        )
    
    try:
        # Retrieve payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_confirmation.payment_intent_id)
        
        if intent.status != 'succeeded':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not successful"
            )
        
        # Get booking details
        booking_id = int(intent.metadata['booking_id'])
        stmt = select(Booking).where(
            and_(
                Booking.id == booking_id,
                Booking.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check if payment already exists
        stmt = select(Payment).where(
            and_(
                Payment.booking_id == booking_id,
                Payment.stripe_payment_id == intent.id
            )
        )
        result = await db.execute(stmt)
        existing_payment = result.scalar_one_or_none()
        
        if existing_payment:
            return existing_payment
        
        # Create payment record
        db_payment = Payment(
            booking_id=booking_id,
            user_id=current_user.id,
            amount=Decimal(intent.amount) / 100,  # Convert from cents
            currency=intent.currency.upper(),
            payment_method=PaymentMethod.STRIPE,
            payment_status=PaymentStatus.COMPLETED,
            stripe_payment_id=intent.id,
            stripe_charge_id=intent.charges.data[0].id if intent.charges.data else None
        )
        
        db.add(db_payment)
        
        # Update booking status
        booking.status = 'confirmed'
        db.add(booking)
        
        await db.commit()
        await db.refresh(db_payment)
        
        return db_payment
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment confirmation error: {str(e)}"
        )


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Payment]:
    """List current user's payments."""
    
    stmt = select(Payment).where(Payment.user_id == current_user.id)
    result = await db.execute(stmt)
    payments = result.scalars().all()
    
    return list(payments)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Payment:
    """Get payment by ID (user's own payments only)."""
    
    stmt = select(Payment).where(
        and_(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


# Ecocash Payment Endpoints

@router.post("/ecocash/create", response_model=EcocashPaymentResponse)
async def create_ecocash_payment(
    payment_request: EcocashPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> EcocashPaymentResponse:
    """Create an Ecocash payment."""
    
    try:
        # Validate phone number
        if not ecocash_service.validate_phone_number(payment_request.customer_msisdn):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format. Use formats like: 0774222475, 263774222475, or +263774222475"
            )
        
        # Verify booking exists and belongs to user
        booking_stmt = select(Booking).where(
            and_(
                Booking.id == payment_request.booking_id,
                Booking.user_id == current_user.id
            )
        )
        booking_result = await db.execute(booking_stmt)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or you don't have permission to access it"
            )
        
        # Create payment with Ecocash
        response = await ecocash_service.create_payment(
            customer_msisdn=payment_request.customer_msisdn,
            amount=payment_request.amount,
            reason=payment_request.reason,
            currency=payment_request.currency
        )
        
        # Create payment record in database
        payment = Payment(
            booking_id=payment_request.booking_id,
            user_id=current_user.id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            payment_method="ecocash",
            payment_status="pending",
            ecocash_reference=response["source_reference"],
            customer_msisdn=payment_request.customer_msisdn
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        # Prepare response
        success = response["status_code"] == 200
        test_pins = ecocash_service.get_test_pins() if ecocash_service.is_test_environment() else None
        
        return EcocashPaymentResponse(
            status_code=response["status_code"],
            response=response["response"],
            source_reference=response["source_reference"],
            success=success,
            message="Payment created successfully" if success else "Payment failed",
            test_pins=test_pins
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Ecocash payment: {str(e)}"
        )


@router.get("/ecocash/test-info", response_model=EcocashTestInfo)
async def get_ecocash_test_info() -> EcocashTestInfo:
    """Get Ecocash test information for sandbox environment."""
    
    return EcocashTestInfo(
        environment=settings.ECOCASH_ENVIRONMENT,
        test_pins=ecocash_service.get_test_pins(),
        merchant_code=settings.ECOCASH_MERCHANT_CODE,
        api_key_prefix=settings.ECOCASH_API_KEY[:10] + "..."
    )


@router.post("/ecocash/webhook")
async def ecocash_webhook(
    webhook_data: dict,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Handle Ecocash webhook notifications."""
    
    try:
        # Process webhook data
        transaction_id = webhook_data.get("transactionId")
        payment_status = webhook_data.get("status")
        amount = webhook_data.get("amount")
        
        # Update payment in database
        if transaction_id:
            stmt = select(Payment).where(Payment.ecocash_transaction_id == transaction_id)
            result = await db.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if payment:
                payment.payment_status = payment_status
                await db.commit()
        
        return {"status": "webhook processed", "transaction_id": transaction_id}
        
    except Exception as e:
        print(f"❌ Ecocash Webhook Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


# PayPal Payment Endpoints

@router.post("/paypal/create", response_model=PayPalPaymentResponse)
async def create_paypal_payment(
    payment_request: PayPalPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PayPalPaymentResponse:
    """Create PayPal payment."""
    
    try:
        # Verify booking exists and belongs to user
        booking_stmt = select(Booking).where(
            and_(
                Booking.id == payment_request.booking_id,
                Booking.user_id == current_user.id
            )
        )
        booking_result = await db.execute(booking_stmt)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or you don't have permission to access it"
            )
        
        # Create PayPal order
        response = paypal_service.create_order(
            amount=payment_request.amount,
            currency=payment_request.currency,
            description=payment_request.description
        )
        
        if response.get("success"):
            # Create payment record in database
            payment = Payment(
                booking_id=payment_request.booking_id,
                user_id=current_user.id,
                amount=payment_request.amount,
                currency=payment_request.currency,
                payment_method="paypal",
                payment_status="pending",
                paypal_order_id=response.get("response", {}).get("id")
            )
            
            db.add(payment)
            await db.commit()
            await db.refresh(payment)
            
            # Extract approval URL from response
            order_data = response.get("response", {})
            approval_url = None
            for link in order_data.get("links", []):
                if link.get("rel") == "approve":
                    approval_url = link.get("href")
                    break
            
            return PayPalPaymentResponse(
                success=True,
                order_id=order_data.get("id"),
                approval_url=approval_url,
                status_code=response.get("status_code"),
                response=response.get("response"),
                message="PayPal order created successfully"
            )
        else:
            return PayPalPaymentResponse(
                success=False,
                status_code=response.get("status_code"),
                response=response.get("response"),
                message="Failed to create PayPal order"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PayPal payment creation failed: {str(e)}"
        )


@router.get("/paypal/test-info", response_model=PayPalTestInfo)
async def get_paypal_test_info():
    """Get PayPal test information."""
    
    try:
        test_info = paypal_service.get_test_info()
        return PayPalTestInfo(**test_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get PayPal test info: {str(e)}"
        )


@router.post("/paypal/webhook")
async def handle_paypal_webhook(
    webhook_data: PayPalWebhook,
    db: AsyncSession = Depends(get_db)
):
    """Handle PayPal webhook notifications."""
    
    try:
        # Process webhook data
        event_type = webhook_data.event_type
        resource = webhook_data.resource
        
        # Handle payment completion
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            order_id = resource.get("id")
            payment_status = "completed"
            amount = resource.get("amount", {}).get("value")
            
            # Update payment in database
            if order_id:
                stmt = select(Payment).where(Payment.paypal_order_id == order_id)
                result = await db.execute(stmt)
                payment = result.scalar_one_or_none()
                
                if payment:
                    payment.payment_status = payment_status
                    payment.paypal_payment_status = event_type
                    await db.commit()
        
        return {"status": "webhook processed", "event_type": event_type}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PayPal webhook processing failed: {str(e)}"
        )


@router.get("/paypal/order/{order_id}")
async def get_paypal_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get PayPal order details."""
    
    try:
        response = paypal_service.get_order_details(order_id)
        
        if response.get("success"):
            return {
                "success": True,
                "order_details": response.get("response"),
                "status_code": response.get("status_code")
            }
        else:
            return {
                "success": False,
                "error": "Failed to get PayPal order details",
                "response": response.get("response")
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get PayPal order: {str(e)}"
        )


@router.post("/paypal/capture/{order_id}")
async def capture_paypal_payment(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Capture PayPal payment."""
    
    try:
        response = paypal_service.capture_payment(order_id)
        
        if response.get("success"):
            # Update payment status
            capture_data = response.get("response", {})
            payment_status = "completed"
            
            # Find and update payment
            stmt = select(Payment).where(Payment.paypal_order_id == order_id)
            result = await db.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if payment:
                payment.payment_status = payment_status
                payment.paypal_capture_id = capture_data.get("id")
                await db.commit()
            
            return {
                "success": True,
                "capture_id": capture_data.get("id"),
                "status": capture_data.get("status"),
                "amount": capture_data.get("amount"),
                "message": "Payment captured successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to capture PayPal payment",
                "response": response.get("response")
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture PayPal payment: {str(e)}"
        )
        
    except Exception as e:
        print(f"❌ Ecocash Webhook Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )
