import requests

def test_lockout_status():
    """Test if the account is already locked after previous failed attempts."""
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔒 Testing Lockout Status")
    print("=" * 50)
    
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing lockout status for user: {test_username}")
    print("Making one more login attempt...")
    
    # Test with curl
    import subprocess
    curl_command = [
        "curl", "-X", "POST",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-d", f"username={test_username}&password={test_password}",
        login_url
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = result.stdout
            print(f"Response status: {result.returncode}")
            print(f"Response body: {response}")
            
            if "Account locked" in response:
                print(f"   🎉 RATE LIMITING WORKING! Account is locked!")
                print(f"   Response: {response}")
                return True
            elif "401 Unauthorized" in response:
                print(f"   Still getting 401 - account not locked yet")
                print(f"   Response: {response}")
                return False
            else:
                print(f"   Unexpected response: {response}")
        else:
            print(f"   Curl error: {result.stderr}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    return False

if __name__ == "__main__":
    test_lockout_status()
