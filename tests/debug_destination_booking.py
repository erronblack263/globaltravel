import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db, engine
from models.user import User
from models.destination import Destination
from models.booking import Booking
from datetime import date, timedelta

async def debug_destination_booking():
    """Debug destination booking creation step by step."""
    
    print("🔍 Debugging Destination Booking Creation")
    print("=" * 50)
    
    async with engine.begin() as conn:
        # Create a session
        async with AsyncSession(conn, expire_on_commit=False) as db:
            
            # Step 1: Get a test user
            print("\n1. Getting test user...")
            user_stmt = select(User).where(User.username == "string")
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                print("   ❌ Test user 'string' not found")
                return
            print(f"   ✅ Found user: {user.username} (ID: {user.id})")
            
            # Step 2: Get a destination
            print("\n2. Getting destination...")
            dest_stmt = select(Destination).limit(1)
            dest_result = await db.execute(dest_stmt)
            destination = dest_result.scalar_one_or_none()
            
            if not destination:
                print("   ❌ No destinations found")
                return
            print(f"   ✅ Found destination: {destination.name} (ID: {destination.id})")
            print(f"   Entry fee: ${destination.entry_fee}")
            
            # Step 3: Calculate total amount
            print("\n3. Calculating total amount...")
            guests = 2
            total_amount = destination.entry_fee * guests
            print(f"   Entry fee: ${destination.entry_fee}")
            print(f"   Guests: {guests}")
            print(f"   Total amount: ${total_amount}")
            
            # Step 4: Create booking object
            print("\n4. Creating booking object...")
            try:
                booking = Booking(
                    user_id=user.id,
                    booking_type="destination",
                    destination_id=destination.id,
                    resort_id=None,
                    check_in_date=date.today() + timedelta(days=7),
                    check_out_date=None,  # Day trip
                    number_of_guests=guests,
                    special_requests="Test booking",
                    total_amount=total_amount,
                    status="pending"
                )
                print("   ✅ Booking object created successfully")
                print(f"   Booking type: {booking.booking_type}")
                print(f"   Destination ID: {booking.destination_id}")
                print(f"   Resort ID: {booking.resort_id}")
                print(f"   Total amount: {booking.total_amount}")
            except Exception as e:
                print(f"   ❌ Error creating booking object: {e}")
                return
            
            # Step 5: Save to database
            print("\n5. Saving to database...")
            try:
                db.add(booking)
                await db.commit()
                await db.refresh(booking)
                print(f"   ✅ Booking saved successfully!")
                print(f"   Booking ID: {booking.id}")
                print(f"   UUID: {booking.uuid}")
            except Exception as e:
                print(f"   ❌ Error saving booking: {e}")
                await db.rollback()
                return
            
            print("\n🎉 Destination booking created successfully!")

if __name__ == "__main__":
    asyncio.run(debug_destination_booking())
