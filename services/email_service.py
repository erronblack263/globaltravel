from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

from core.config import settings


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_TLS=settings.MAIL_TLS,
            MAIL_SSL=settings.MAIL_SSL,
            MAIL_STARTTLS=True
        )
        
        # Setup Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        self.fm = FastMail(self.conf)
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user."""
        
        try:
            message = MessageSchema(
                subject="Welcome to Global Travel!",
                recipients=[user_email],
                template_body={
                    "user_name": user_name,
                    "app_name": settings.APP_NAME
                },
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name="welcome.html")
            return True
            
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
    
    async def send_booking_confirmation(
        self,
        user_email: str,
        user_name: str,
        booking_details: dict
    ) -> bool:
        """Send booking confirmation email."""
        
        try:
            message = MessageSchema(
                subject="Booking Confirmation - Global Travel",
                recipients=[user_email],
                template_body={
                    "user_name": user_name,
                    "booking": booking_details,
                    "app_name": settings.APP_NAME
                },
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name="booking_confirmation.html")
            return True
            
        except Exception as e:
            print(f"Failed to send booking confirmation email: {e}")
            return False
    
    async def send_payment_confirmation(
        self,
        user_email: str,
        user_name: str,
        payment_details: dict
    ) -> bool:
        """Send payment confirmation email."""
        
        try:
            message = MessageSchema(
                subject="Payment Confirmation - Global Travel",
                recipients=[user_email],
                template_body={
                    "user_name": user_name,
                    "payment": payment_details,
                    "app_name": settings.APP_NAME
                },
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name="payment_confirmation.html")
            return True
            
        except Exception as e:
            print(f"Failed to send payment confirmation email: {e}")
            return False
    
    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email."""
        
        try:
            reset_link = f"{settings.APP_URL}/reset-password?token={reset_token}"
            
            message = MessageSchema(
                subject="Password Reset - Global Travel",
                recipients=[user_email],
                template_body={
                    "user_name": user_name,
                    "reset_link": reset_link,
                    "app_name": settings.APP_NAME
                },
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name="password_reset.html")
            return True
            
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
    
    async def send_booking_cancellation(
        self,
        user_email: str,
        user_name: str,
        booking_details: dict
    ) -> bool:
        """Send booking cancellation email."""
        
        try:
            message = MessageSchema(
                subject="Booking Cancelled - Global Travel",
                recipients=[user_email],
                template_body={
                    "user_name": user_name,
                    "booking": booking_details,
                    "app_name": settings.APP_NAME
                },
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name="booking_cancellation.html")
            return True
            
        except Exception as e:
            print(f"Failed to send booking cancellation email: {e}")
            return False
    
    async def send_promotional_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        template_data: dict
    ) -> bool:
        """Send promotional email to multiple recipients."""
        
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=template_data,
                subtype="html"
            )
            
            await self.fm.send_message(message, template_name=template_name)
            return True
            
        except Exception as e:
            print(f"Failed to send promotional email: {e}")
            return False
