"""
Database migration script to add PayNow columns to payments table
"""

import asyncio
import asyncpg
from sqlalchemy import text
from core.database import engine

async def add_paynow_columns():
    """Add PayNow columns to payments table"""
    
    # SQL commands to add PayNow columns
    sql_commands = [
        """
        ALTER TABLE payments 
        ADD COLUMN IF NOT EXISTS paynow_reference VARCHAR(255),
        ADD COLUMN IF NOT EXISTS paynow_poll_url VARCHAR(500),
        ADD COLUMN IF NOT EXISTS paynow_redirect_url VARCHAR(500),
        ADD COLUMN IF NOT EXISTS paynow_transaction_id VARCHAR(255)
        """,
        """
        ALTER TABLE payments 
        ADD COLUMN IF NOT EXISTS ecocash_transaction_id VARCHAR(255),
        ADD COLUMN IF NOT EXISTS ecocash_reference VARCHAR(255),
        ADD COLUMN IF NOT EXISTS customer_msisdn VARCHAR(20)
        """
    ]
    
    async with engine.begin() as conn:
        for sql in sql_commands:
            try:
                await conn.execute(text(sql))
                print(f"✅ Successfully executed: {sql[:50]}...")
            except Exception as e:
                print(f"❌ Error executing SQL: {e}")
    
    print("🎉 PayNow columns migration completed!")

async def check_columns():
    """Check if columns exist in payments table"""
    
    check_sql = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'payments' 
    AND column_name IN ('paynow_reference', 'paynow_poll_url', 'paynow_redirect_url', 'paynow_transaction_id')
    ORDER BY column_name
    """
    
    async with engine.begin() as conn:
        result = await conn.execute(text(check_sql))
        columns = result.fetchall()
        
        print("📋 Current PayNow columns in payments table:")
        for column in columns:
            print(f"  ✅ {column[0]}: {column[1]}")
        
        if not columns:
            print("  ❌ No PayNow columns found")

if __name__ == "__main__":
    print("🔄 Starting PayNow columns migration...")
    
    # Run the migration
    asyncio.run(add_paynow_columns())
    
    # Check the results
    asyncio.run(check_columns())
    
    print("✅ Migration completed!")
