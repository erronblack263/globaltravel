"""
Database migration script to make booking_id nullable in payments table.
Run this script to update your database schema.
"""

import asyncio
from sqlalchemy import text
from core.database import engine

async def make_booking_nullable():
    """Make booking_id nullable in payments table."""
    
    print("🔧 Making booking_id nullable in payments table...")
    
    try:
        async with engine.begin() as conn:
            # Drop foreign key constraint first
            print("   Dropping foreign key constraint...")
            await conn.execute(text("""
                ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_booking_id_fkey
            """))
            
            # Make the column nullable
            print("   Making booking_id nullable...")
            await conn.execute(text("""
                ALTER TABLE payments ALTER COLUMN booking_id DROP NOT NULL
            """))
            
            # Re-add foreign key constraint (now nullable)
            print("   Re-adding foreign key constraint...")
            await conn.execute(text("""
                ALTER TABLE payments ADD CONSTRAINT payments_booking_id_fkey 
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
            """))
        
        print("\n🎉 booking_id is now nullable!")
        print("   - Payments can now be created without linking to a booking")
        print("   - Foreign key constraint preserved for data integrity")
        
    except Exception as e:
        print(f"\n❌ Error making booking_id nullable: {str(e)}")
        print("   Please check your database connection and permissions")
        raise

async def check_booking_nullable():
    """Check if booking_id is nullable in payments table."""
    
    print("🔍 Checking if booking_id is nullable...")
    
    try:
        async with engine.begin() as conn:
            # Check if column is nullable
            result = await conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'payments' 
                AND column_name = 'booking_id'
            """))
            
            nullable = result.scalar()
            
            print(f"   booking_id nullable: {nullable}")
            
            if nullable == 'YES':
                print("   ✅ booking_id is nullable!")
                return True
            else:
                print("   ❌ booking_id is still NOT nullable")
                return False
                
    except Exception as e:
        print(f"❌ Error checking nullable: {str(e)}")
        return False

async def main():
    """Main migration function."""
    
    print("🗄️  Make booking_id Nullable Migration")
    print("=" * 50)
    
    # Check if booking_id is already nullable
    is_nullable = await check_booking_nullable()
    
    if not is_nullable:
        print("\n🔧 Running migration...")
        await make_booking_nullable()
        
        # Verify the change
        await check_booking_nullable()
    else:
        print("\n✅ Migration already completed!")
    
    print("\n" + "=" * 50)
    print("🎯 Migration complete! Standalone Ecocash payments are now supported.")

if __name__ == "__main__":
    asyncio.run(main())
