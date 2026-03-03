import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db, engine
from models.user import User
from models.booking import Booking
from models.destination import Destination
from models.resort import Resort
from datetime import datetime, timedelta

async def create_test_booking():
    """Create a test booking for Ecocash payment testing."""
    
    print("🏨 Creating Test Booking for Ecocash Payment")
    print("=" * 50)
    
    async with engine.begin() as conn:
        # Create a session
        async with AsyncSession(conn, expire_on_commit=False) as db:
            
            # Get a test user
            user_stmt = select(User).where(User.username == "string")
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                print("❌ Test user 'string' not found. Please create a user first.")
                return None
            
            print(f"✅ Found user: {user.username} (ID: {user.id})")
            
            # Get a destination
            dest_stmt = select(Destination).limit(1)
            dest_result = await db.execute(dest_stmt)
            destination = dest_result.scalar_one_or_none()
            
            if not destination:
                print("❌ No destinations found. Please create a destination first.")
                return None
            
            print(f"✅ Found destination: {destination.name}")
            
            # Get a resort
            resort_stmt = select(Resort).limit(1)
            resort_result = await db.execute(resort_stmt)
            resort = resort_result.scalar_one_or_none()
            
            if not resort:
                print("❌ No resorts found. Please create a resort first.")
                return None
            
            print(f"✅ Found resort: {resort.name}")
            
            # Create test booking
            booking = Booking(
                user_id=user.id,
                destination_id=destination.id,
                resort_id=resort.id,
                check_in_date=datetime.now() + timedelta(days=7),
                check_out_date=datetime.now() + timedelta(days=10),
                guests=2,
                total_amount=150.00,
                status="pending",
                payment_status="unpaid"
            )
            
            db.add(booking)
            await db.commit()
            await db.refresh(booking)
            
            print(f"🎉 Test booking created successfully!")
            print(f"   Booking ID: {booking.id}")
            print(f"   User: {user.username}")
            print(f"   Destination: {destination.name}")
            print(f"   Resort: {resort.name}")
            print(f"   Amount: ${booking.total_amount}")
            print(f"   Status: {booking.status}")
            
            return booking

async def main():
    """Main function to create test booking."""
    
    booking = await create_test_booking()
    
    if booking:
        print("\n" + "=" * 50)
        print("🎯 Ready to test Ecocash payment!")
        print(f"   Use booking_id: {booking.id}")
        print(f"   Amount: ${booking.total_amount}")
        print("\n📱 Test Payment Request:")
        print(f"""{{
  "booking_id": {booking.id},
  "customer_msisdn": "0774222475",
  "amount": {booking.total_amount},
  "reason": "Global Travel Booking",
  "currency": "USD"
}}""")
    else:
        print("\n❌ Could not create test booking")

if __name__ == "__main__":
    asyncio.run(main())
