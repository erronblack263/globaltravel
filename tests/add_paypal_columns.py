"""
Database migration script to add PayPal columns to payments table.
Run this script to update your database schema.
"""

import asyncio
from sqlalchemy import text
from core.database import engine

async def add_paypal_columns():
    """Add PayPal columns to payments table."""
    
    print("🔧 Adding PayPal columns to payments table...")
    
    # SQL statements to add PayPal columns
    sql_statements = [
        """
        ALTER TABLE payments 
        ADD COLUMN IF NOT EXISTS paypal_order_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS paypal_capture_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS paypal_payer_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS paypal_payer_email VARCHAR(255),
        ADD COLUMN IF NOT EXISTS paypal_payment_status VARCHAR(50)
        """,
        
        """
        COMMENT ON COLUMN payments.paypal_order_id IS 'PayPal order ID for payment tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.paypal_capture_id IS 'PayPal capture ID for payment tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.paypal_payer_id IS 'PayPal payer ID for customer tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.paypal_payer_email IS 'PayPal payer email for customer tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.paypal_payment_status IS 'PayPal payment status for tracking'
        """
    ]
    
    try:
        async with engine.begin() as conn:
            for i, statement in enumerate(sql_statements):
                print(f"   Executing statement {i+1}/{len(sql_statements)}...")
                await conn.execute(text(statement))
                print(f"   ✅ Statement {i+1} completed")
        
        print("\n🎉 PayPal columns added successfully!")
        print("   - paypal_order_id: VARCHAR(255)")
        print("   - paypal_capture_id: VARCHAR(255)")
        print("   - paypal_payer_id: VARCHAR(255)")
        print("   - paypal_payer_email: VARCHAR(255)")
        print("   - paypal_payment_status: VARCHAR(50)")
        
    except Exception as e:
        print(f"\n❌ Error adding PayPal columns: {str(e)}")
        print("   Please check your database connection and permissions")
        raise

async def check_paypal_columns_exist():
    """Check if PayPal columns exist in payments table."""
    
    print("🔍 Checking if PayPal columns exist...")
    
    try:
        async with engine.begin() as conn:
            # Check if columns exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'payments' 
                AND column_name IN ('paypal_order_id', 'paypal_capture_id', 'paypal_payer_id', 'paypal_payer_email', 'paypal_payment_status')
            """))
            
            columns = [row[0] for row in result.fetchall()]
            
            print(f"   Found columns: {columns}")
            
            expected_columns = ['paypal_order_id', 'paypal_capture_id', 'paypal_payer_id', 'paypal_payer_email', 'paypal_payment_status']
            missing_columns = [col for col in expected_columns if col not in columns]
            
            if missing_columns:
                print(f"   Missing columns: {missing_columns}")
                return False
            else:
                print("   ✅ All PayPal columns exist!")
                return True
                
    except Exception as e:
        print(f"❌ Error checking columns: {str(e)}")
        return False

async def main():
    """Main migration function."""
    
    print("🗄️  PayPal Database Migration")
    print("=" * 50)
    
    # Check if columns already exist
    columns_exist = await check_paypal_columns_exist()
    
    if not columns_exist:
        print("\n🔧 Running migration...")
        await add_paypal_columns()
        
        # Verify columns were added
        await check_paypal_columns_exist()
    else:
        print("\n✅ Migration already completed!")
    
    print("\n" + "=" * 50)
    print("🎯 Migration complete! Your database is ready for PayPal payments.")

if __name__ == "__main__":
    asyncio.run(main())
