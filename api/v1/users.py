from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

from core.database import get_db
from core.dependancies import get_current_active_user
from models.user import User
from schemas.user import UserResponse
from core.security import get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["users"])

class UserProfile(BaseModel):
    """User profile information."""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordChangeResponse(BaseModel):
    """Password change response."""
    message: str
    success: bool

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user profile information."""
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone_number=current_user.phone_number,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Change user password."""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = get_password_hash(password_data.new_password)
    
    # Update password
    current_user.password_hash = new_password_hash
    await db.commit()
    
    return PasswordChangeResponse(
        message="Password changed successfully",
        success=True
    )

@router.get("/settings", response_model=dict)
async def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get user settings information."""
    
    return {
        "profile": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone_number": current_user.phone_number,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat()
        },
        "settings": {
            "allow_email_notifications": True,
            "allow_push_notifications": True,
            "theme": "light",
            "language": "en"
        }
    }
