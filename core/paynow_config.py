"""
PayNow Payment Gateway Configuration
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class PayNowConfig:
    """PayNow configuration settings."""
    
    # PayNow API Credentials
    merchant_id: str
    merchant_key: str
    integration_id: str
    integration_key: str
    
    # Payment Settings
    return_url: str
    result_url: str
    auth_email: Optional[str] = None
    
    # API Endpoints
    base_url: str = "https://www.paynow.co.zw"
    initiate_url: str = "https://www.paynow.co.zw/interface/InitiateTransaction"
    poll_url: str = "https://www.paynow.co.zw/interface/TransactionStatus"
    
    # Supported Methods
    supported_methods: list = None
    
    def __post_init__(self):
        if self.supported_methods is None:
            self.supported_methods = [
                "ecocash",      # Mobile money
                "onemoney",     # Mobile money  
                "telecash",     # Mobile money
                "zipit",        # Bank transfer
                "mastercard",   # Credit card
                "visacard",     # Credit card
                "banktransfer"  # Bank transfer
            ]
    
    @classmethod
    def from_env(cls) -> 'PayNowConfig':
        """Load configuration from environment variables."""
        return cls(
            merchant_id=os.getenv("PAYNOW_MERCHANT_ID", ""),
            merchant_key=os.getenv("PAYNOW_MERCHANT_KEY", ""),
            integration_id=os.getenv("PAYNOW_INTEGRATION_ID", ""),
            integration_key=os.getenv("PAYNOW_INTEGRATION_KEY", ""),
            return_url=os.getenv("PAYNOW_RETURN_URL", "http://localhost:8000/api/v1/payments/return"),
            result_url=os.getenv("PAYNOW_RESULT_URL", "http://localhost:8000/api/v1/payments/webhook"),
            auth_email=os.getenv("PAYNOW_AUTH_EMAIL")
        )
    
    def is_configured(self) -> bool:
        """Check if PayNow is properly configured."""
        return bool(
            self.merchant_id and 
            self.merchant_key and 
            self.integration_id and 
            self.integration_key
        )

# Global configuration instance
paynow_config = PayNowConfig.from_env()
