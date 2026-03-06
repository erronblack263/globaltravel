import http.client
import json
import uuid
from typing import Dict, Any, Optional
from core.config import settings


class PayPalService:
    """PayPal payment service for Global Travel application."""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.sandbox = getattr(settings, 'PAYPAL_SANDBOX', True)
        self.base_url = getattr(settings, 'PAYPAL_BASE_URL', 'https://sandbox.paypal.com')
        
    def get_base_url(self) -> str:
        """Get PayPal base URL based on environment."""
        if self.sandbox:
            return "https://api-m.sandbox.paypal.com"
        else:
            return "https://api-m.paypal.com"
    
    def get_access_token(self) -> Dict[str, Any]:
        """Get PayPal access token."""
        try:
            hostname = "api-m.sandbox.paypal.com" if self.sandbox else "api-m.paypal.com"
            print(f"🔍 Using Token Hostname: {hostname}")
            conn = http.client.HTTPSConnection(hostname)
            
            # Prepare auth data
            auth_string = f"{self.client_id}:{self.client_secret}"
            import base64
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Request access token
            conn.request("POST", "/v1/oauth2/token", "grant_type=client_credentials", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            if response.status == 200:
                return json.loads(data)
            else:
                print(f"❌ PayPal Token Error: {response.status} - {data}")
                return {"error": data}
                
        except Exception as e:
            print(f"❌ PayPal Token Exception: {str(e)}")
            return {"error": str(e)}
    
    def create_order(self, amount: float, currency: str = "USD", description: str = "Global Travel Booking") -> Dict[str, Any]:
        """Create PayPal order."""
        try:
            # Get access token
            token_response = self.get_access_token()
            if "error" in token_response:
                return {
                    "success": False,
                    "error": "Failed to get access token",
                    "details": token_response
                }
            
            access_token = token_response.get("access_token")
            
            # Create order
            hostname = "api-m.sandbox.paypal.com" if self.sandbox else "api-m.paypal.com"
            print(f"🔍 Using Hostname: {hostname}")
            conn = http.client.HTTPSConnection(hostname)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'PayPal-Request-Id': str(uuid.uuid4())
            }
            
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": str(uuid.uuid4()),
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    }
                }],
                "application_context": {
                    "brand_name": "Global Travel",
                    "landing_page": "BILLING",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "PAY_NOW",
                    "return_url": "http://127.0.0.1:8000/api/v1/payments/paypal/success",
                    "cancel_url": "http://127.0.0.1:8000/api/v1/payments/paypal/cancel"
                }
            }
            
            conn.request("POST", "/v2/checkout/orders", json.dumps(payload), headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            response_data = {
                "status_code": response.status,
                "response": json.loads(data) if data else {},
                "success": response.status == 201
            }
            
            # Log the response
            print(f"🔍 PayPal Order Response: {response.status}")
            print(f"🔍 Response Data: {data}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ PayPal Order Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create PayPal order"
            }
    
    def capture_payment(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal payment."""
        try:
            # Get access token
            token_response = self.get_access_token()
            if "error" in token_response:
                return {
                    "success": False,
                    "error": "Failed to get access token"
                }
            
            access_token = token_response.get("access_token")
            
            # Capture payment
            hostname = "api-m.sandbox.paypal.com" if self.sandbox else "api-m.paypal.com"
            conn = http.client.HTTPSConnection(hostname)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            conn.request("POST", f"/v2/checkout/orders/{order_id}/capture", "", headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            response_data = {
                "status_code": response.status,
                "response": json.loads(data) if data else {},
                "success": response.status == 201
            }
            
            print(f"🔍 PayPal Capture Response: {response.status}")
            print(f"🔍 Capture Data: {data}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ PayPal Capture Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to capture PayPal payment"
            }
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get PayPal order details."""
        try:
            # Get access token
            token_response = self.get_access_token()
            if "error" in token_response:
                return {
                    "success": False,
                    "error": "Failed to get access token"
                }
            
            access_token = token_response.get("access_token")
            
            # Get order details
            hostname = "api-m.sandbox.paypal.com" if self.sandbox else "api-m.paypal.com"
            conn = http.client.HTTPSConnection(hostname)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            conn.request("GET", f"/v2/checkout/orders/{order_id}", headers=headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            response_data = {
                "status_code": response.status,
                "response": json.loads(data) if data else {},
                "success": response.status == 200
            }
            
            return response_data
            
        except Exception as e:
            print(f"❌ PayPal Order Details Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get PayPal order details"
            }
    
    def is_test_environment(self) -> bool:
        """Check if running in test environment."""
        return self.sandbox
    
    def get_test_info(self) -> Dict[str, Any]:
        """Get PayPal test information."""
        return {
            "environment": "sandbox" if self.sandbox else "production",
            "base_url": self.get_base_url(),
            "test_mode": self.is_test_environment(),
            "test_accounts": {
                "buyer": "personal-buyer@sandbox.com",
                "password": "Test123456",
                "seller": "business-seller@sandbox.com",
                "password": "Test123456"
            },
            "test_cards": [
                {
                    "number": "4111111111111111",
                    "type": "visa",
                    "expires": "12/2025",
                    "cvv": "123"
                },
                {
                    "number": "5555555555554444",
                    "type": "mastercard", 
                    "expires": "12/2025",
                    "cvv": "123"
                }
            ]
        }


# PayPal service instance
paypal_service = PayPalService()
