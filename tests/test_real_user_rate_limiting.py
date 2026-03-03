import subprocess
import time

def test_real_user_rate_limiting():
    """Test rate limiting with real user 'string' from database."""
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔒 Testing Rate Limiting with Real User 'string'")
    print("=" * 50)
    
    # Test with real user from database
    test_username = "string"
    test_password = "wrongpassword"
    
    print(f"Testing with real user: {test_username}")
    print("Making 5 login attempts with wrong password...")
    
    for i in range(5):
        print(f"\nAttempt {i+1}: Sending wrong password...")
        
        # Use curl to send form data exactly as FastAPI expects
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
                
                if "Account locked" in response:
                    print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                    print(f"   Response: {response}")
                    print("\n" + "=" * 50)
                    print("✅ RATE LIMITING IS WORKING!")
                    print("Your security system is properly protecting against brute force attacks!")
                    return True
                elif "401 Unauthorized" in response:
                    print(f"   Regular 401 response")
                else:
                    print(f"   Response: {response}")
            else:
                print(f"   ❌ Curl error: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between attempts
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("Rate limiting test completed.")
    return False

if __name__ == "__main__":
    success = test_real_user_rate_limiting()
    if success:
        print("\n🎉 SUCCESS! Rate limiting is working correctly!")
    else:
        print("\n🔍 Rate limiting test failed - check server logs for debug info")
