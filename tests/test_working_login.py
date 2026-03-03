import subprocess
import json

def test_working_login():
    """Test the working login endpoint with proper JSON."""
    
    print("🔒 Testing Working Login Endpoint")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing login with user: {test_username}")
    print("Using proper JSON format...")
    
    # Create proper JSON data
    json_data = {
        "username": test_username,
        "password": test_password
    }
    
    # Convert to JSON string for curl
    json_string = json.dumps(json_data)
    
    print(f"JSON data: {json_string}")
    
    # Use curl with proper JSON
    curl_command = [
        "curl", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json_string,
        login_url
    ]
    
    print(f"Curl command: {' '.join(curl_command)}")
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)
        
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            response = result.stdout
            
            if "Account locked" in response:
                print("   🎉 RATE LIMITING WORKING! Account locked message detected!")
                print(f"   Response: {response}")
                return True
            elif "429" in response:
                print("   🎉 RATE LIMITING WORKING! Got 429 Too Many Requests!")
                print(f"   Response: {response}")
                return True
            elif "401" in response:
                print("   Got 401 - account not locked yet")
                print(f"   Response: {response}")
            else:
                print(f"   Unexpected response: {response}")
        else:
            print(f"   Curl failed: {result.stderr}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    return False

if __name__ == "__main__":
    test_working_login()
