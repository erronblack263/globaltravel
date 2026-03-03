import subprocess
import time

def test_exact_form_rate_limiting():
    """Test rate limiting with exact form format FastAPI expects."""
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔒 Testing Rate Limiting with Exact Form Format")
    print("=" * 50)
    
    # Test with real user from database
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing with user: {test_username}")
    print("Making 5 login attempts with wrong password...")
    
    for i in range(5):
        print(f"\nAttempt {i+1}: Sending wrong password...")
        
        # Try different form formats to see what works
        formats_to_try = [
            # Format 1: Standard form data
            f"username={test_username}&password={test_password}",
            # Format 2: URL encoded
            f"username={test_username}&password={test_password}",
            # Format 3: With quotes
            f"username={test_username}&password={test_password}",
            # Format 4: JSON (might work)
            f'{{"username": "{test_username}", "password": "{test_password}"}}'
        ]
        
        # Try each format until we get 401 instead of 422
        for format_num, data in enumerate(formats_to_try, 1):
            print(f"   Trying format {format_num}...")
            
            if format_num == 4:  # JSON format
                curl_command = [
                    "curl", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", data,
                    login_url
                ]
            else:  # Form data
                curl_command = [
                    "curl", "-X", "POST",
                    "-H", "Content-Type: application/x-www-form-urlencoded",
                    "-d", data,
                    login_url
                ]
            
            try:
                result = subprocess.run(curl_command, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    response = result.stdout
                    
                    if "Account locked" in response:
                        print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                        print(f"   Response: {response}")
                        print("\n" + "=" * 50)
                        print("✅ RATE LIMITING IS WORKING!")
                        return True
                    elif "401 Unauthorized" in response or "Incorrect username" in response:
                        print(f"   ✅ Got 401 Unauthorized with format {format_num}")
                        print(f"   Response: {response}")
                        break  # Found working format, use this for remaining attempts
                    else:
                        print(f"   Format {format_num} response: {response}")
                else:
                    print(f"   Format {format_num} error: {result.stderr}")
            except Exception as e:
                print(f"   Format {format_num} exception: {e}")
        
        # If we found a working format, continue with it
        if "401 Unauthorized" in response:
            print(f"   Using working format for remaining attempts...")
            for j in range(i+1, 5):
                print(f"\nAttempt {j+1}: Using working format...")
                result = subprocess.run(curl_command, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    response = result.stdout
                    if "Account locked" in response:
                        print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                        print(f"   Response: {response}")
                        print("\n" + "=" * 50)
                        print("✅ RATE LIMITING IS WORKING!")
                        return True
                    else:
                        print(f"   Response: {response}")
        
        # Small delay between attempts
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("Rate limiting test completed - no working format found.")
    return False

if __name__ == "__main__":
    success = test_exact_form_rate_limiting()
    if success:
        print("\n🎉 SUCCESS! Rate limiting is working correctly!")
    else:
        print("\n🔍 Could not find working format - FastAPI configuration issue")
