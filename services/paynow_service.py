"""
PayNow Payment Service
"""

import hashlib
import uuid
import requests
from typing import Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from urllib.parse import urlencode

from core.paynow_config import paynow_config
from models.payment import Payment
from models.booking import Booking
from schemas.payment import PaymentCreate, PaymentResponse, PaymentStatus

class PayNowService:
    """PayNow payment processing service."""
    
    def __init__(self):
        self.config = paynow_config
        self.session = requests.Session()
    
    def generate_hash(self, data: Dict[str, str]) -> str:
        """Generate PayNow hash for security."""
        # Sort keys alphabetically
        sorted_keys = sorted(data.keys())
        
        # Create hash string
        hash_string = ""
        for key in sorted_keys:
            if data[key]:
                hash_string += data[key]
        
        # Add integration key
        hash_string += self.config.integration_key
        
        # Generate SHA512 hash
        return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
    
    async def initiate_payment(
        self, 
        booking: Booking, 
        payment_data: PaymentCreate
    ) -> Tuple[bool, Optional[Dict]]:
        """Initiate payment with PayNow."""
        
        if not self.config.is_configured():
            return False, {"error": "PayNow not configured"}
        
        # Prepare payment data
        payment_data_dict = {
            "id": self.config.merchant_id,
            "reference": f"BOOK-{booking.id}-{uuid.uuid4().hex[:8]}",
            "amount": str(booking.total_amount),
            "additionalinfo": f"Payment for booking #{booking.id}",
            "returnurl": self.config.return_url,
            "resulturl": self.config.result_url,
            "authemail": self.config.auth_email or "",
            "status": "Message"
        }
        
        # Generate hash
        payment_data_dict["hash"] = self.generate_hash(payment_data_dict)
        
        try:
            # Make API call
            response = self.session.post(
                self.config.initiate_url,
                data=payment_data_dict,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if payment was initiated successfully
                if result.get("status") == "Ok":
                    return True, result
                else:
                    return False, {"error": result.get("error", "Payment initiation failed")}
            else:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
    
    async def check_payment_status(self, poll_url: str, reference: str) -> Tuple[bool, Optional[Dict]]:
        """Check payment status using poll URL."""
        
        try:
            # Prepare status check data
            status_data = {
                "id": self.config.merchant_id,
                "reference": reference,
                "hash": self.generate_hash({
                    "id": self.config.merchant_id,
                    "reference": reference
                })
            }
            
            # Make API call
            response = self.session.post(
                poll_url,
                data=status_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
    
    def map_paynow_status(self, paynow_status: str) -> PaymentStatus:
        """Map PayNow status to our PaymentStatus enum."""
        status_mapping = {
            "Paid": PaymentStatus.COMPLETED,
            "Awaiting Delivery": PaymentStatus.PENDING,
            "Delivered": PaymentStatus.COMPLETED,
            "Cancelled": PaymentStatus.CANCELLED,
            "Created": PaymentStatus.PENDING,
            "Message": PaymentStatus.PENDING,
            "Sent": PaymentStatus.PENDING
        }
        
        return status_mapping.get(paynow_status, PaymentStatus.PENDING)
    
    def get_payment_method_info(self, method: str) -> Dict[str, str]:
        """Get payment method information."""
        method_info = {
            "ecocash": {
                "name": "EcoCash",
                "description": "Mobile money transfer",
                "icon": "mobile",
                "type": "mobile_money"
            },
            "onemoney": {
                "name": "OneMoney",
                "description": "Mobile money transfer", 
                "icon": "mobile",
                "type": "mobile_money"
            },
            "telecash": {
                "name": "TeleCash",
                "description": "Mobile money transfer",
                "icon": "mobile", 
                "type": "mobile_money"
            },
            "zipit": {
                "name": "ZIPIT",
                "description": "Bank transfer",
                "icon": "bank",
                "type": "bank_transfer"
            },
            "mastercard": {
                "name": "MasterCard",
                "description": "Credit/Debit card",
                "icon": "card",
                "type": "card"
            },
            "visacard": {
                "name": "Visa",
                "description": "Credit/Debit card",
                "icon": "card",
                "type": "card"
            },
            "banktransfer": {
                "name": "Bank Transfer",
                "description": "Direct bank transfer",
                "icon": "bank",
                "type": "bank_transfer"
            }
        }
        
        return method_info.get(method, {
            "name": method,
            "description": "Payment method",
            "icon": "payment",
            "type": "other"
        })

# Global service instance
paynow_service = PayNowService()
