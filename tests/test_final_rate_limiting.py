import requests
import json
import time
import random
import string

def test_final_rate_limiting():
    """Final test of rate limiting with unique user each time."""
    
    base_url = "http://127.0.0.1:8000"
    register_url = f"{base_url}/api/v1/auth/register"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔒 Final Rate Limiting Test")
    print("=" * 50)
    
    # Generate unique user for this test
    random_num = random.randint(1000, 9999)
    test_username = f"testuser{random_num}"
    test_email = f"testuser{random_num}@example.com"
    test_password = "wrongpassword"
    
    print(f"Testing with unique user: {test_username}")
    
    # Step 1: Register unique user
    print("\n1. Registering unique user...")
    register_data = {
        "email": test_email,
        "username": test_username,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(register_url, json=register_data)
        if register_response.status_code == 201:
            print("   ✅ User registered successfully")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Small delay
    time.sleep(1)
    
    # Step 2: Test rate limiting with this unique user
    print(f"\n2. Testing rate limiting with {test_username}...")
    print("Making 5 login attempts with wrong password...")
    
    for i in range(5):
        print(f"\nAttempt {i+1}: Sending wrong password...")
        
        data = {
            "username": test_username,
            "password": test_password
        }
        
        try:
            response = requests.post(login_url, data=data, headers={
                "Content-Type": "application/x-www-form-urlencoded"
            })
            
            if response.status_code == 401:
                response_text = response.text
                
                if "locked" in response_text.lower():
                    print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                    print(f"   Response: {response_text}")
                    print("\n" + "=" * 50)
                    print("✅ RATE LIMITING IS WORKING!")
                    print("Your security system is properly protecting against brute force attacks!")
                    return True
                else:
                    print(f"   Regular 401 response: {response_text}")
            elif response.status_code == 429:
                print(f"   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests")
                print(f"   Response: {response.text}")
                return True
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between attempts
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("❌ Rate limiting test completed - no lockout detected")
    print("This might indicate:")
    print("1. User registration failed (user already exists)")
    print("2. Rate limiting logic needs debugging")
    print("3. Database user lookup issues")
    return False

if __name__ == "__main__":
    success = test_final_rate_limiting()
    if success:
        print("\n🎉 SUCCESS! Rate limiting is working correctly!")
    else:
        print("\n🔍 Rate limiting needs investigation")
