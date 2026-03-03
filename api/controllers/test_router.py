from fastapi import APIRouter

# Create a separate test router
test_router = APIRouter(
    prefix="/api/v1/test",
    tags=["Tests"]
)

@test_router.get("/test-endpoint", tags=["Tests"])
async def test_endpoint():
    """Simple test endpoint to verify router is working."""
    return {"message": "Test router endpoint working", "status": "success"}

@test_router.get("/another-test", tags=["Tests"])
async def another_test():
    """Another test endpoint."""
    return {"message": "Another test endpoint working", "router": "test_router"}

@test_router.get("/basic-test", tags=["Tests"])
async def basic_test():
    """Basic test endpoint with no dependencies."""
    return {"message": "Basic test endpoint working", "status": "success"}

@test_router.post("/test-login-rate-limiting", tags=["Tests"])
async def test_login_rate_limiting(
    username: str = None,
    password: str = None
):
    """Test endpoint to verify rate limiting is working."""
    
    # Use provided parameters or defaults
    test_username = username or "string"
    test_password = password or "wrongpassword"
    
    print(f"🔍 Testing rate limiting for user: {test_username}")
    
    # Simulate 3 failed attempts
    from core.security import record_failed_login, is_account_locked, get_lockout_remaining_time
    
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
        "attempts_recorded": 3,
        "test_username": test_username,
        "test_password": test_password
    }
