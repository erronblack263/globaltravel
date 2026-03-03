"""
Database migration script to add Ecocash columns to payments table.
Run this script to update your database schema.
"""

import asyncio
from sqlalchemy import text
from core.database import engine

async def add_ecocash_columns():
    """Add Ecocash columns to payments table."""
    
    print("🔧 Adding Ecocash columns to payments table...")
    
    # SQL statements to add Ecocash columns
    sql_statements = [
        """
        ALTER TABLE payments 
        ADD COLUMN IF NOT EXISTS ecocash_transaction_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS ecocash_reference VARCHAR(255),
        ADD COLUMN IF NOT EXISTS customer_msisdn VARCHAR(20)
        """,
        
        """
        COMMENT ON COLUMN payments.ecocash_transaction_id IS 'Ecocash transaction ID for payment tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.ecocash_reference IS 'Ecocash reference number for payment tracking'
        """,
        
        """
        COMMENT ON COLUMN payments.customer_msisdn IS 'Customer phone number for Ecocash payments'
        """
    ]
    
    try:
        async with engine.begin() as conn:
            for i, statement in enumerate(sql_statements):
                print(f"   Executing statement {i+1}/{len(sql_statements)}...")
                await conn.execute(text(statement))
                print(f"   ✅ Statement {i+1} completed")
        
        print("\n🎉 Ecocash columns added successfully!")
        print("   - ecocash_transaction_id: VARCHAR(255)")
        print("   - ecocash_reference: VARCHAR(255)")
        print("   - customer_msisdn: VARCHAR(20)")
        
    except Exception as e:
        print(f"\n❌ Error adding Ecocash columns: {str(e)}")
        print("   Please check your database connection and permissions")
        raise

async def check_columns_exist():
    """Check if Ecocash columns exist in payments table."""
    
    print("🔍 Checking if Ecocash columns exist...")
    
    try:
        async with engine.begin() as conn:
            # Check if columns exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'payments' 
                AND column_name IN ('ecocash_transaction_id', 'ecocash_reference', 'customer_msisdn')
            """))
            
            columns = [row[0] for row in result.fetchall()]
            
            print(f"   Found columns: {columns}")
            
            expected_columns = ['ecocash_transaction_id', 'ecocash_reference', 'customer_msisdn']
            missing_columns = [col for col in expected_columns if col not in columns]
            
            if missing_columns:
                print(f"   Missing columns: {missing_columns}")
                return False
            else:
                print("   ✅ All Ecocash columns exist!")
                return True
                
    except Exception as e:
        print(f"❌ Error checking columns: {str(e)}")
        return False

async def main():
    """Main migration function."""
    
    print("🗄️  Ecocash Database Migration")
    print("=" * 50)
    
    # Check if columns already exist
    columns_exist = await check_columns_exist()
    
    if not columns_exist:
        print("\n🔧 Running migration...")
        await add_ecocash_columns()
        
        # Verify columns were added
        await check_columns_exist()
    else:
        print("\n✅ Migration already completed!")
    
    print("\n" + "=" * 50)
    print("🎯 Migration complete! Your database is ready for Ecocash payments.")

if __name__ == "__main__":
    asyncio.run(main())
