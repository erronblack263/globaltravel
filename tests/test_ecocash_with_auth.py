import requests
import json
import uuid

def get_auth_token(base_url="http://127.0.0.1:8000"):
    """Get authentication token by logging in."""
    
    print("🔐 Getting Authentication Token...")
    
    # Login credentials (use your existing user)
    login_data = {
        "username": "string",  # Replace with your username
        "password": "string"   # Replace with your password
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   ✅ Authentication successful!")
            return token
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_ecocash_with_auth():
    """Test Ecocash payment with authentication."""
    
    print("💳 Ecocash Payment Integration Test (With Auth)")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Get authentication token
    token = get_auth_token(base_url)
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test Ecocash Payment Creation
    print("\n2. Creating Ecocash Payment (With Authentication)...")
    payment_data = {
        "customer_msisdn": "263774222475",
        "amount": 10.50,
        "reason": "Global Travel Test Booking",
        "currency": "USD"
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/payments/ecocash/create",
            json=payment_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            payment_response = response.json()
            print(f"   ✅ Payment created successfully!")
            print(f"   Source Reference: {payment_response['source_reference']}")
            print(f"   Test PINs: {payment_response.get('test_pins', [])}")
            print(f"   Success: {payment_response['success']}")
        else:
            print(f"   ❌ Payment creation failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Complete!")
    print("   - Authentication: ✅ Working")
    print("   - Ecocash Integration: Ready to test")
    print("   - Next: Test with real phone numbers in sandbox")

if __name__ == "__main__":
    test_ecocash_with_auth()
