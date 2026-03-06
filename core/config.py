from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/globaltravel"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Account Lockout Settings
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # PayPal
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_SANDBOX: bool = True
    PAYPAL_BASE_URL: str = "https://sandbox.paypal.com"
    PAYPAL_WEBHOOK_URL: Optional[str] = None
    PAYPAL_ENVIRONMENT: str = "sandbox"
    
    # PayNow
    PAYNOW_MERCHANT_ID: Optional[str] = None
    PAYNOW_MERCHANT_KEY: Optional[str] = None
    PAYNOW_INTEGRATION_ID: Optional[str] = None
    PAYNOW_INTEGRATION_KEY: Optional[str] = None
    PAYNOW_RETURN_URL: Optional[str] = None
    PAYNOW_RESULT_URL: Optional[str] = None
    PAYNOW_AUTH_EMAIL: Optional[str] = None
    
    # Unsplash
    UNSPLASH_ACCESS_KEY: Optional[str] = None
    UNSPLASH_SECRET_KEY: Optional[str] = None
    UNSPLASH_APP_ID: Optional[str] = None
    UNSPLASH_BASE_URL: Optional[str] = None
    
    # Email
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Ecocash Configuration
    ECOCASH_API_KEY: str = "WtSY2sm-AeEWn-iELJuNWnIyFGYctSNu"
    ECOCASH_MERCHANT_CODE: str = "08658"
    ECOCASH_BASE_URL: str = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v2"
    ECOCASH_SANDBOX_URL: str = "https://developers.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b/sandbox"
    ECOCASH_PRODUCTION_URL: str = "https://api.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b"
    ECOCASH_ENVIRONMENT: str = "sandbox"
    
    # Application
    APP_NAME: str = "Global Travel"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
