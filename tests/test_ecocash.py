import requests
import json
import uuid

def test_ecocash_integration():
    """Test Ecocash payment integration."""
    
    print("💳 Ecocash Payment Integration Test")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Get Ecocash Test Info
    print("\n1. Getting Ecocash Test Information...")
    try:
        response = requests.get(f"{base_url}/api/v1/payments/ecocash/test-info")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            test_info = response.json()
            print(f"   Environment: {test_info['environment']}")
            print(f"   Test PINs: {test_info['test_pins']}")
            print(f"   Merchant Code: {test_info['merchant_code']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create Ecocash Payment
    print("\n2. Creating Ecocash Payment...")
    payment_data = {
        "customer_msisdn": "263774222475",
        "amount": 10.50,
        "reason": "Global Travel Test Booking",
        "currency": "USD"
    }
    
    try:
        # First, try without authentication (should fail with 401)
        response = requests.post(
            f"{base_url}/api/v1/payments/ecocash/create",
            json=payment_data
        )
        print(f"   Status (no auth): {response.status_code}")
        print(f"   Response (no auth): {json.dumps(response.json(), indent=2)}")
        
        # Note: You'll need to get a valid JWT token by logging in first
        print("   🔍 To test with authentication:")
        print("      1. Login to get JWT token")
        print("      2. Add token to Authorization header")
        print("      3. Retry the request")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Manual Ecocash API Test
    print("\n3. Testing Ecocash API Directly...")
    try:
        # Generate unique UUID for each test
        unique_reference = str(uuid.uuid4())
        
        ecocash_payload = {
            "customerMsisdn": "263774222475",
            "amount": 10.50,
            "reason": "Global Travel Test",
            "currency": "USD",
            "sourceReference": unique_reference
        }
        
        headers = {
            'X-API-KEY': 'WtSY2sm-AeEWn-iELJuNWnIyFGYctSNu',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "https://developers.ecocash.co.zw/api/ecocash_pay/api/v2/payment/instant/c2b/sandbox",
            json=ecocash_payload,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print(f"   Generated UUID: {unique_reference}")
        
        if response.status_code == 200:
            print("   ✅ Direct Ecocash API working!")
        else:
            print(f"   ❌ Direct Ecocash API failed")
            print(f"   🔍 Try again with a new UUID (they're unique per request)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   - Test 1: Verify Ecocash configuration")
    print("   - Test 2: Test payment creation through API")
    print("   - Test 3: Test direct Ecocash API connection")
    print("   - Use test PINs: 0000, 1234, 9999 for sandbox")

if __name__ == "__main__":
    test_ecocash_integration()
