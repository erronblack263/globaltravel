import requests
import json

def test_endpoint_debug():
    """Test if the login endpoint is being called at all."""
    
    print("🔍 Testing Login Endpoint Debug")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing login endpoint with user: {test_username}")
    print("Check your server console for debug messages...")
    
    json_data = {
        "username": test_username,
        "password": test_password
    }
    
    try:
        print(f"\nSending request to: {login_url}")
        print(f"Request data: {json_data}")
        
        response = requests.post(login_url, json=json_data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 401:
            print("\n❌ Got 401 - Check server console for debug messages:")
            print("   - 🔍 DEBUG: Login attempt for username: string")
            print("   - 🔍 DEBUG: User found: True")
            print("   - 🔍 DEBUG: Checking lockout for username: string")
            print("   - 🔍 DEBUG: Username locked: True")
            print("   - 🔍 DEBUG: ACCOUNT LOCKED!")
            
            if "Account locked" in response.text:
                print("   🎉 RATE LIMITING WORKING!")
            else:
                print("   ❌ Still getting regular 401 - endpoint not checking lockout")
        elif response.status_code == 429:
            print("\n🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
        else:
            print(f"\n❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 If you don't see debug messages in server console, the endpoint isn't being called!")

if __name__ == "__main__":
    test_endpoint_debug()
