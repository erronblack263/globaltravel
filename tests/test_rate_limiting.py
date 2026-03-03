import asyncio
import aiohttp
import json
from datetime import datetime

async def test_rate_limiting():
    """Test rate limiting with same user multiple times."""
    
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔒 Testing Rate Limiting with Same User")
    print("=" * 50)
    
    # Test user credentials
    test_username = "test@example.com"
    wrong_password = "wrongpassword"
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    print(f"Testing with user: {test_username}")
    print("Making 5 login attempts with wrong password...")
    
    for i in range(5):
        print(f"\nAttempt {i+1}: Sending wrong password...")
        
        data = f"username={test_username}&password={wrong_password}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(login_url, data=data, headers=headers) as response:
                    if response.status == 401:
                        print(f"   ✅ Got 401 Unauthorized (expected)")
                        
                        # Check if it's a lockout message
                        response_text = await response.text()
                        if "locked" in response_text.lower():
                            print(f"   🎉 RATE LIMITING WORKING! Account locked message detected")
                            print(f"   Response: {response_text}")
                        else:
                            print(f"   Regular 401 response")
                    else:
                        print(f"   ❌ Unexpected status: {response.status}")
                        print(f"   Response: {await response.text()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between attempts
        await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Rate Limiting Test Complete!")
    print("If you saw 'Account locked' message, rate limiting is working!")
    print("If you only saw regular 401 messages, there might be an issue.")

if __name__ == "__main__":
    asyncio.run(test_rate_limiting())
