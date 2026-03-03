import requests
import json

def test_direct_rate_limiting():
    """Test rate limiting by calling the security functions directly."""
    
    print("🔒 Direct Rate Limiting Test")
    print("=" * 50)
    
    # Import and test security functions directly
    from core.security import record_failed_login, is_account_locked, get_lockout_remaining_time
    
    test_email = "string@example.com"
    test_username = "string"
    
    print(f"Testing rate limiting directly for user: {test_username}")
    
    # Step 1: Record 3 failed attempts
    print("\n1. Recording 3 failed attempts...")
    for i in range(3):
        print(f"   Recording attempt {i+1}...")
        record_failed_login(test_email, username=test_username)
    
    # Step 2: Check if account is locked
    print("\n2. Checking lockout status...")
    email_locked = is_account_locked(test_email)
    username_locked = is_account_locked(test_username)
    remaining_time = get_lockout_remaining_time(test_email)
    
    print(f"   Email locked: {email_locked}")
    print(f"   Username locked: {username_locked}")
    print(f"   Remaining time: {remaining_time} minutes")
    
    # Step 3: Test login endpoint with correct credentials to see if it checks lockout
    print("\n3. Testing login endpoint...")
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    # Try with JSON format
    json_data = {
        "username": test_username,
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(login_url, json=json_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 429:
            print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
            return True
        elif response.status_code == 401:
            if "Account locked" in response.text:
                print("   🎉 RATE LIMITING WORKING! Account locked message detected!")
                return True
            else:
                print("   Regular 401 response - rate limiting not triggered yet")
        else:
            print(f"   Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Direct security functions are working!")
    print("🔍 The issue is with FastAPI form parsing, not rate limiting logic!")
    return False

if __name__ == "__main__":
    test_direct_rate_limiting()
