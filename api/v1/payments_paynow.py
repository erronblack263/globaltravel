"""
PayNow Payment Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from decimal import Decimal

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from models.payment import Payment
from models.booking import Booking
from schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentUpdate,
    PaymentMethod, PaymentStatus, PayNowPaymentResponse
)
from services.paynow_service import paynow_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/paynow/initiate", response_model=PayNowPaymentResponse)
async def initiate_paynow_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Initiate PayNow payment (supports EcoCash)."""
    
    try:
        # Validate booking exists and belongs to user
        stmt = select(Booking).where(
            and_(
                Booking.id == payment_data.booking_id,
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
        existing_payment = await db.execute(
            select(Payment).where(
                and_(
                    Payment.booking_id == payment_data.booking_id,
                    Payment.payment_status == "completed"
                )
            )
        )
        if existing_payment.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already completed for this booking"
            )
        
        # Initiate PayNow payment
        success, paynow_response = await paynow_service.initiate_payment(booking, payment_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PayNow payment initiation failed: {paynow_response.get('error', 'Unknown error')}"
            )
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=booking.total_amount,
            currency="USD",
            payment_method=payment_data.payment_method.value,
            payment_status="pending",
            paynow_reference=paynow_response.get("reference"),
            paynow_poll_url=paynow_response.get("pollurl"),
            paynow_redirect_url=paynow_response.get("redirecturl"),
            paynow_transaction_id=paynow_response.get("reference")
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        return PayNowPaymentResponse(
            success=True,
            reference=paynow_response.get("reference"),
            poll_url=paynow_response.get("pollurl"),
            redirect_url=paynow_response.get("redirecturl"),
            paynow_reference=paynow_response.get("reference"),
            amount=booking.total_amount,
            payment_method=payment_data.payment_method
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate PayNow payment: {str(e)}"
        )


@router.get("/paynow/status/{reference}")
async def check_paynow_status(
    reference: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check PayNow payment status."""
    
    try:
        # Find payment
        stmt = select(Payment).where(
            and_(
                Payment.paynow_reference == reference,
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
        
        # Check status with PayNow
        success, status_response = await paynow_service.check_payment_status(
            payment.paynow_poll_url, reference
        )
        
        if success:
            # Update payment status
            paynow_status = status_response.get("status", "Message")
            payment.payment_status = paynow_service.map_paynow_status(paynow_status).value
            await db.commit()
            
            return {
                "success": True,
                "payment_status": payment.payment_status,
                "paynow_status": paynow_status,
                "status_response": status_response
            }
        else:
            return {
                "success": False,
                "error": status_response.get("error", "Failed to check status")
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check PayNow status: {str(e)}"
        )


@router.post("/paynow/webhook")
async def paynow_webhook(
    webhook_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Handle PayNow webhook notifications."""
    
    try:
        reference = webhook_data.get("reference")
        status = webhook_data.get("status")
        
        if not reference or not status:
            return {"success": False, "error": "Invalid webhook data"}
        
        # Find payment
        stmt = select(Payment).where(Payment.paynow_reference == reference)
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return {"success": False, "error": "Payment not found"}
        
        # Update payment status
        payment.payment_status = paynow_service.map_paynow_status(status).value
        await db.commit()
        
        return {"success": True, "message": "Webhook processed"}
        
    except Exception as e:
        return {"success": False, "error": f"Webhook processing failed: {str(e)}"}


@router.get("/paynow/methods")
async def get_paynow_methods():
    """Get supported PayNow payment methods."""
    
    try:
        methods = []
        for method in paynow_service.config.supported_methods:
            method_info = paynow_service.get_payment_method_info(method)
            methods.append({
                "method": method,
                **method_info
            })
        
        return {
            "success": True,
            "methods": methods,
            "total_methods": len(methods)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment methods: {str(e)}"
        )
