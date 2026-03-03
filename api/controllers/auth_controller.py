from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Any

from core.database import get_db
from core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    get_password_hash, 
    verify_token,
    record_failed_login,
    clear_login_attempts,
    is_account_locked,
    get_lockout_remaining_time
)
from core.config import settings
from core.dependancies import get_current_user
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin, PasswordChange
from schemas.token import Token, TokenResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    
    # Check if user already exists
    stmt = select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Authenticate user and return tokens with rate limiting and account lockout."""
    
    print("🚨 LOGIN ENDPOINT CALLED!")
    print(f"🔍 DEBUG: Login attempt for username: {form_data.username}")
    
    # Find user by username or email
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    print(f"🔍 DEBUG: User found: {user is not None}")
    
    # Check if account is locked FIRST (before any other logic)
    print(f"🔍 DEBUG: Checking lockout for username: {form_data.username}")
    
    # Check both username and potential email lockout
    username_locked = is_account_locked(form_data.username)
    email_locked = is_account_locked(form_data.username) if "@" in form_data.username else False
    
    print(f"🔍 DEBUG: Username locked: {username_locked}, Email locked: {email_locked}")
    
    if username_locked or email_locked:
        remaining_minutes = get_lockout_remaining_time(form_data.username)
        print(f"🔍 DEBUG: ACCOUNT LOCKED! Remaining minutes: {remaining_minutes}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked due to too many failed attempts. Try again in {remaining_minutes} minutes.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"🔍 DEBUG: Account not locked, proceeding with login...")
    
    # Check credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        # Record failed attempt with both email and username
        if user:
            print(f"🔍 DEBUG: Recording failed login for email: {user.email}, username: {form_data.username}")
            record_failed_login(user.email, username=form_data.username)
        else:
            print(f"🔍 DEBUG: User not found for username: {form_data.username}")
            record_failed_login(None, username=form_data.username)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Clear failed login attempts on successful login
    clear_login_attempts(user.email)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    
    try:
        payload = verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user exists and is active
        stmt = select(User).where(User.id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Change user password."""
    
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/test-debug")
async def test_debug():
    """Test endpoint to verify server is running updated code."""
    return {"message": "Debug test working", "timestamp": "2026-03-01"}


@router.post("/test-login-rate-limiting")
async def test_login_rate_limiting():
    """Test endpoint to verify rate limiting is working."""
    
    # Simulate 3 failed attempts
    from core.security import record_failed_login, is_account_locked, get_lockout_remaining_time
    
    test_username = "string"
    test_email = "string@example.com"
    
    print("🔍 Simulating 3 failed attempts...")
    for i in range(3):
        record_failed_login(test_email, username=test_username)
        print(f"   Attempt {i+1} recorded")
    
    # Check if account is locked
    username_locked = is_account_locked(test_username)
    email_locked = is_account_locked(test_email)
    remaining_time = get_lockout_remaining_time(test_username)
    
    print(f"🔍 Account locked: {username_locked or email_locked}")
    print(f"🔍 Remaining time: {remaining_time} minutes")
    
    return {
        "message": "Rate limiting test endpoint working",
        "tests": "comprehensive",
        "account_locked": username_locked or email_locked,
        "remaining_minutes": remaining_time,
        "attempts_recorded": 3
    }

@router.get("/simple-test")
async def simple_test():
    """Simple test endpoint to verify Swagger UI is working."""
    return {"message": "Simple test endpoint working", "timestamp": "2026-03-01"}

@router.get("/basic-test")
async def basic_test():
    """Basic test endpoint with no dependencies."""
    return {"message": "Basic test endpoint working", "status": "success"}
