"""
Test the filter endpoint directly.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.v1.destinations import router

# Create test app
app = FastAPI()
app.include_router(router, prefix="/api/v1")

def test_filter_endpoint():
    """Test if filter endpoint is accessible."""
    
    with TestClient(app) as client:
        try:
            # Test the filter endpoint
            response = client.get("/api/v1/destinations/filter?destination=cairo&country=egypt")
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Filter endpoint is working!")
            elif response.status_code == 422:
                print("❌ 422 Error - Validation issue")
            elif response.status_code == 401:
                print("❌ 401 Error - Authentication issue")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_filter_endpoint()
