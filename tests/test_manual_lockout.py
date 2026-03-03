import requests
import json

def test_manual_lockout():
    """Manually trigger lockout and test endpoint."""
    
    print("🔒 Manual Lockout Test")
    print("=" * 50)
    
    # Step 1: Manually trigger lockout
    from core.security import record_failed_login, is_account_locked, get_lockout_remaining_time
    
    test_username = "string"
    test_email = "string@example.com"
    
    print("1. Manually triggering 3 failed attempts...")
    for i in range(3):
        record_failed_login(test_email, username=test_username)
        print(f"   Attempt {i+1} recorded")
    
    # Check lockout status
    print("\n2. Checking lockout status...")
    email_locked = is_account_locked(test_email)
    username_locked = is_account_locked(test_username)
    remaining_time = get_lockout_remaining_time(test_email)
    
    print(f"   Email locked: {email_locked}")
    print(f"   Username locked: {username_locked}")
    print(f"   Remaining time: {remaining_time} minutes")
    
    # Step 2: Test login endpoint
    print("\n3. Testing login endpoint...")
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
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
                print("   ❌ Still getting 401 - endpoint not checking lockout!")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 If you're still getting 401, the endpoint is not checking lockout properly!")
    return False

if __name__ == "__main__":
    test_manual_lockout()
