import requests
import json

def test_comprehensive_login():
    """Test login endpoint with rate limiting under tests header."""
    
    print("🔒 Comprehensive Login Test with Rate Limiting")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    test_url = f"{base_url}/api/v1/auth/test-login-rate-limiting"
    
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing user: {test_username}")
    print("This test includes rate limiting validation...")
    
    # Test 1: First login attempt (should get 401)
    print("\n1. First login attempt...")
    json_data = {"username": test_username, "password": test_password}
    
    try:
        response = requests.post(login_url, json=json_data, headers={"X-Tests": "rate-limiting"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Got expected 401 - first attempt")
        elif response.status_code == 429:
            print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Second login attempt (should get 401)
    print("\n2. Second login attempt...")
    try:
        response = requests.post(login_url, json=json_data, headers={"X-Tests": "rate-limiting"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Got expected 401 - second attempt")
        elif response.status_code == 429:
            print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Third login attempt (should get 401)
    print("\n3. Third login attempt...")
    try:
        response = requests.post(login_url, json=json_data, headers={"X-Tests": "rate-limiting"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Got expected 401 - third attempt")
        elif response.status_code == 429:
            print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Fourth login attempt (should get 429 - RATE LIMITED!)
    print("\n4. Fourth login attempt (SHOULD TRIGGER RATE LIMITING!)...")
    try:
        response = requests.post(login_url, json=json_data, headers={"X-Tests": "rate-limiting"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ❌ Still getting 401 - rate limiting NOT working!")
        elif response.status_code == 429:
            print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
            print("   🎉 ACCOUNT LOCKOUT TRIGGERED AFTER 3 FAILED ATTEMPTS!")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   - Attempts 1-3: Should return 401 (wrong password)")
    print("   - Attempt 4: Should return 429 (rate limited)")
    print("   - If you see 429 on attempt 4: RATE LIMITING IS WORKING!")
    print("   - If you see 401 on attempt 4: RATE LIMITING IS NOT WORKING!")
    
    return False

if __name__ == "__main__":
    success = test_comprehensive_login()
    if success:
        print("\n🎉 SUCCESS! Rate limiting is working correctly!")
        print("Your authentication system is properly protecting against brute force attacks!")
    else:
        print("\n🔍 Rate limiting needs investigation")
        print("Check server console for debug messages and error logs")
