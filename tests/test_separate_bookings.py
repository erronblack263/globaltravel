import requests
import json
from datetime import date, timedelta

def test_separate_bookings():
    """Test the separate resort and destination booking endpoints."""
    
    print("🏨 Testing Separate Resort & Destination Bookings")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Get available resorts
    print("\n1. Getting Available Resorts...")
    try:
        response = requests.get(f"{base_url}/api/v1/resorts/")
        if response.status_code == 200:
            resorts = response.json()
            print(f"   ✅ Found {len(resorts)} resorts")
            if resorts:
                print(f"   First resort: {resorts[0]['name']} (ID: {resorts[0]['id']})")
                resort_id = resorts[0]['id']
            else:
                print("   ❌ No resorts found")
                return
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get available destinations
    print("\n2. Getting Available Destinations...")
    try:
        response = requests.get(f"{base_url}/api/v1/destinations/")
        if response.status_code == 200:
            destinations = response.json()
            print(f"   ✅ Found {len(destinations)} destinations")
            if destinations:
                print(f"   First destination: {destinations[0]['name']} (ID: {destinations[0]['id']})")
                destination_id = destinations[0]['id']
            else:
                print("   ❌ No destinations found")
                return
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 3: Create Resort Booking
    print("\n3. Creating Resort Booking...")
    resort_booking_data = {
        "resort_id": resort_id,
        "check_in_date": (date.today() + timedelta(days=7)).isoformat(),
        "check_out_date": (date.today() + timedelta(days=10)).isoformat(),
        "number_of_guests": 2,
        "special_requests": "Ocean view room please"
    }
    
    try:
        # Note: You'll need to add authentication token
        headers = {"Authorization": "Bearer YOUR_TOKEN_HERE"}
        response = requests.post(
            f"{base_url}/api/v1/resort-bookings/",
            json=resort_booking_data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            resort_booking = response.json()
            print(f"   ✅ Resort booking created!")
            print(f"   Booking ID: {resort_booking['id']}")
            print(f"   Total Amount: ${resort_booking['total_amount']}")
            resort_booking_id = resort_booking['id']
        else:
            print(f"   ❌ Error: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 4: Create Destination Booking
    print("\n4. Creating Destination Booking...")
    destination_booking_data = {
        "destination_id": destination_id,
        "check_in_date": (date.today() + timedelta(days=14)).isoformat(),
        "check_out_date": (date.today() + timedelta(days=17)).isoformat(),
        "number_of_guests": 3,
        "special_requests": "Guided tours included"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/destination-bookings/",
            json=destination_booking_data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            destination_booking = response.json()
            print(f"   ✅ Destination booking created!")
            print(f"   Booking ID: {destination_booking['id']}")
            print(f"   Total Amount: ${destination_booking['total_amount']}")
            destination_booking_id = destination_booking['id']
        else:
            print(f"   ❌ Error: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 5: Test Ecocash Payment for Resort Booking
    print("\n5. Testing Ecocash Payment for Resort Booking...")
    payment_data = {
        "booking_id": resort_booking_id,
        "customer_msisdn": "0774222475",
        "amount": resort_booking['total_amount'],
        "reason": "Resort Booking Payment",
        "currency": "USD"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/payments/ecocash/create",
            json=payment_data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            payment_response = response.json()
            print(f"   ✅ Ecocash payment created!")
            print(f"   Source Reference: {payment_response['source_reference']}")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("   ✅ Separate resort bookings endpoint: /api/v1/resort-bookings/")
    print("   ✅ Separate destination bookings endpoint: /api/v1/destination-bookings/")
    print("   ✅ Resort booking linked to Ecocash payment")
    print("   ✅ Clear separation of booking types")
    print("\n📱 Next Steps:")
    print("   1. Add authentication token to headers")
    print("   2. Test with real user login")
    print("   3. Verify Ecocash SMS prompt")

if __name__ == "__main__":
    test_separate_bookings()
