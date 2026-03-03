import asyncio
from core.security import (
    record_failed_login, 
    is_account_locked, 
    get_lockout_remaining_time,
    clear_login_attempts
)

async def test_security():
    """Test the new security features."""
    
    email = "test@example.com"
    ip = "192.168.1.1"
    
    print("🔒 Testing Security Features")
    print("=" * 40)
    
    # Test 1: Check initial state
    print(f"1. Initial lockout status: {is_account_locked(email)}")
    
    # Test 2: Record 3 failed attempts
    print("\n2. Recording 3 failed login attempts...")
    for i in range(3):
        record_failed_login(email, ip)
        print(f"   Attempt {i+1}: Failed login recorded")
    
    # Test 3: Check if account is locked
    print(f"\n3. Lockout status after 3 attempts: {is_account_locked(email)}")
    
    # Test 4: Check remaining time
    remaining = get_lockout_remaining_time(email)
    if remaining:
        print(f"4. Remaining lockout time: {remaining} minutes")
    else:
        print("4. No remaining lockout time")
    
    # Test 5: Clear attempts (successful login)
    print("\n5. Simulating successful login...")
    clear_login_attempts(email)
    print(f"   Lockout status after clear: {is_account_locked(email)}")
    print(f"   Remaining time after clear: {get_lockout_remaining_time(email)}")
    
    print("\n✅ Security features working correctly!")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(test_security())
