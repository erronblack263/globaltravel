import requests

def test_final_login():
    """Test the fixed login endpoint."""
    
    print("🔒 Testing Fixed Login Endpoint")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing login with user: {test_username}")
    print("Since account should be locked from previous attempts...")
    
    # Test with different formats to find one that works
    formats_to_try = [
        # Try form data format
        {
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": f"username={test_username}&password={test_password}"
        },
        # Try JSON format  
        {
            "headers": {"Content-Type": "application/json"},
            "json": {"username": test_username, "password": test_password}
        }
    ]
    
    for i, format_config in enumerate(formats_to_try, 1):
        print(f"\nTrying format {i}: {format_config['headers']['Content-Type']}")
        
        try:
            if "json" in format_config:
                response = requests.post(login_url, json=format_config["json"])
            else:
                response = requests.post(login_url, data=format_config["data"], headers=format_config["headers"])
            
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
                    print("   Got 401 - trying next format...")
            else:
                print(f"   Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Test complete. If you see 429 or 'Account locked' message above, rate limiting is working!")
    return False

if __name__ == "__main__":
    test_final_login()
