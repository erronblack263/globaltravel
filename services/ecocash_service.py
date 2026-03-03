import http.client
import json
import uuid
from typing import Dict, Any, Optional
from core.config import settings

class EcocashService:
    """Ecocash payment service integration."""
    
    def __init__(self):
        self.api_key = settings.ECOCASH_API_KEY
        self.merchant_code = settings.ECOCASH_MERCHANT_CODE
        self.base_url = settings.ECOCASH_SANDBOX_URL if settings.ECOCASH_ENVIRONMENT == "sandbox" else settings.ECOCASH_BASE_URL
        self.environment = settings.ECOCASH_ENVIRONMENT
    
    async def create_payment(
        self,
        customer_msisdn: str,
        amount: float,
        reason: str = "Global Travel Booking",
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Create an Ecocash payment.
        
        Args:
            customer_msisdn: Customer phone number (e.g., "263774222475" or "0774222475")
            amount: Payment amount
            reason: Payment description
            currency: Currency code (default: "USD")
        
        Returns:
            Dict with payment response
        """
        
        # Convert phone number to Ecocash format
        formatted_msisdn = self.format_phone_number(customer_msisdn)
        try:
            # Generate unique source reference
            source_reference = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                "customerMsisdn": formatted_msisdn,
                "amount": amount,
                "reason": reason,
                "currency": currency,
                "sourceReference": source_reference
            }
            
            # Make HTTP request
            payment_url = self.get_payment_url()
            conn = http.client.HTTPSConnection(self.get_domain_from_url(payment_url))
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            conn.request("POST", self.get_path_from_url(payment_url), 
                        json.dumps(payload), headers)
            
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            # Parse response
            response_data = {
                "status_code": response.status,
                "response": json.loads(data) if data else {},
                "source_reference": source_reference
            }
            
            # Log the response
            print(f"🔍 Ecocash Payment Response: {response.status}")
            print(f"🔍 Response Data: {data}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ Ecocash Payment Error: {str(e)}")
            return {
                "status_code": 500,
                "response": {"error": str(e)},
                "source_reference": source_reference if 'source_reference' in locals() else None
            }
    
    async def check_payment_status(self, source_reference: str) -> Dict[str, Any]:
        """
        Check payment status using source reference.
        
        Args:
            source_reference: Unique payment reference
        
        Returns:
            Dict with payment status
        """
        try:
            # This would typically be a GET request to check status
            # For now, return a mock response
            return {
                "status": "pending",
                "source_reference": source_reference,
                "message": "Payment status check not implemented yet"
            }
        except Exception as e:
            print(f"❌ Ecocash Status Check Error: {str(e)}")
            return {"error": str(e)}
    
    def is_test_environment(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "sandbox"
    
    def get_payment_url(self) -> str:
        """Get the appropriate payment URL based on environment."""
        if self.environment == "sandbox":
            return "https://developers.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b/sandbox"
        elif self.environment == "production":
            return "https://api.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b"
        else:
            # Default to sandbox
            return "https://developers.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b/sandbox"
    
    def get_test_pins(self) -> list:
        """Get test PIN codes for sandbox environment."""
        if self.is_test_environment():
            return ["0000", "1234", "9999"]
        return []
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to Ecocash MSISDN format.
        
        Args:
            phone_number: Phone number in various formats (e.g., "0774222475", "263774222475", "+263774222475")
        
        Returns:
            Formatted phone number in Ecocash format (e.g., "263774222475")
        """
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different formats
        if clean_number.startswith('263'):
            # Already in international format
            return clean_number
        elif clean_number.startswith('0'):
            # Local format (e.g., 0774222475 -> 263774222475)
            return '263' + clean_number[1:]
        elif clean_number.startswith('+263'):
            # International format with + (e.g., +263774222475 -> 263774222475)
            return clean_number[1:]
        else:
            # Assume it's already in the correct format or handle as needed
            return clean_number
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            True if valid, False otherwise
        """
        formatted = self.format_phone_number(phone_number)
        # Ecocash numbers should be 12 digits (263 + 9-digit number)
        return len(formatted) == 12 and formatted.startswith('263')
    
    def get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        if "sandbox" in url:
            return "developers.ecocash.co.zw"
        else:
            return "api.ecocash.co.zw"
    
    def get_path_from_url(self, url: str) -> str:
        """Extract path from URL."""
        if "sandbox" in url:
            return "/api/ecocash_pay/api/v2/payment/instant/c2b/sandbox"
        else:
            return "/api/ecocash_pay/api/v2/payment/instant/c2b"

# Ecocash service instance
ecocash_service = EcocashService()
