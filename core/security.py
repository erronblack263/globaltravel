from datetime import datetime, timedelta
from typing import Optional, Union, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(token: str) -> int:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(user_id)


def generate_password_reset_token(email: str) -> str:
    """Generate password reset token."""
    delta = timedelta(hours=1)  # Token valid for 1 hour
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token."""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None


# Login attempt tracking (in production, use Redis)
# Using global variables for persistence across requests
login_attempts: Dict[str, list] = {}
locked_accounts: Dict[str, datetime] = {}

# Initialize with some test data to simulate persistence
def initialize_test_data():
    """Initialize with test data for demonstration."""
    # This simulates having some failed attempts already
    login_attempts["test@example.com"] = []

def record_failed_login(email: str, ip_address: str = None, username: str = None) -> None:
    """Record failed login attempt."""
    # Track by email and username for flexibility
    identifiers = [email, username] if email and username else [email or username]
    
    print(f"🔍 DEBUG: Recording failed login for identifiers: {identifiers}")
    print(f"🔍 DEBUG: Current login_attempts: {login_attempts}")
    
    for identifier in identifiers:
        if identifier and identifier not in login_attempts:
            login_attempts[identifier] = []
    
    # Add failed attempt with timestamp and IP for each identifier
    for identifier in identifiers:
        if identifier:
            login_attempts[identifier].append({
                "timestamp": datetime.utcnow(),
                "ip": ip_address
            })
    
    # Clean old attempts (older than 1 hour) for all identifiers
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    for identifier in identifiers:
        if identifier in login_attempts:
            login_attempts[identifier] = [
                attempt for attempt in login_attempts[identifier]
                if attempt["timestamp"] > cutoff_time
            ]
    
    # Check if account should be locked (check all identifiers)
    for identifier in identifiers:
        if identifier and len(login_attempts[identifier]) >= settings.MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            locked_accounts[identifier] = lock_until
            print(f"🔍 DEBUG: LOCKING ACCOUNT {identifier} until {lock_until}")
    
    print(f"🔍 DEBUG: Updated login_attempts: {login_attempts}")
    print(f"🔍 DEBUG: Updated locked_accounts: {locked_accounts}")

def clear_login_attempts(email: str) -> None:
    """Clear login attempts after successful login."""
    if email in login_attempts:
        del login_attempts[email]
    if email in locked_accounts:
        del locked_accounts[email]

def is_account_locked(email: str) -> bool:
    """Check if account is locked."""
    if email not in locked_accounts:
        return False
    
    lock_until = locked_accounts[email]
    if datetime.utcnow() < lock_until:
        return True
    else:
        # Lock expired, remove from locked accounts
        del locked_accounts[email]
        return False

def get_lockout_remaining_time(email: str) -> Optional[int]:
    """Get remaining lockout time in minutes."""
    if email not in locked_accounts:
        return None
    
    lock_until = locked_accounts[email]
    remaining = lock_until - datetime.utcnow()
    
    if remaining.total_seconds() > 0:
        return int(remaining.total_seconds() / 60)
    else:
        del locked_accounts[email]
        return None