import requests
import json
import time

def test_complete_rate_limiting():
    """Complete test: Register user, then test rate limiting."""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔒 Complete Rate Limiting Test")
    print("=" * 50)
    
    # Step 1: Register a test user first
    print("\n1. Registering test user...")
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data)
        if register_response.status_code == 201:
            print("   ✅ User registered successfully")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Step 2: Test rate limiting with the registered user
    print("\n2. Testing rate limiting with registered user...")
    login_url = f"{base_url}/api/v1/auth/login"
    
    test_username = "testuser"
    wrong_password = "wrongpassword"
    
    for i in range(5):
        print(f"\nAttempt {i+1}: Sending wrong password for {test_username}...")
        
        # Use form data properly
        data = {
            "username": test_username,
            "password": wrong_password
        }
        
        try:
            response = requests.post(login_url, data=data)
            
            if response.status_code == 401:
                print(f"   ✅ Got 401 Unauthorized")
                
                # Check if it's a lockout message
                response_text = response.text
                if "locked" in response_text.lower():
                    print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                    print(f"   Response: {response_text}")
                    print("\n" + "=" * 50)
                    print("✅ RATE LIMITING IS WORKING!")
                    print("Your security system is properly protecting against brute force attacks!")
                    return
                else:
                    print(f"   Regular 401 response")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between attempts
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("❌ Rate limiting test failed - no lockout message detected")
    print("The user might not exist or there's an issue with the rate limiting logic.")

if __name__ == "__main__":
    test_complete_rate_limiting()
