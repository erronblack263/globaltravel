from core.security import login_attempts, locked_accounts, is_account_locked, get_lockout_remaining_time
from datetime import datetime

def debug_rate_limiting():
    """Debug the current state of rate limiting system."""
    
    print("🔍 Rate Limiting System Debug")
    print("=" * 50)
    
    # Show current state
    print(f"Current login_attempts: {login_attempts}")
    print(f"Current locked_accounts: {locked_accounts}")
    
    # Test specific user
    test_email = "string@example.com"
    test_username = "string"
    
    print(f"\nTesting user: {test_username}")
    print(f"Email locked: {is_account_locked(test_email)}")
    print(f"Username locked: {is_account_locked(test_username)}")
    print(f"Remaining time: {get_lockout_remaining_time(test_email)} minutes")
    
    # Check if we have any failed attempts recorded
    if test_username in login_attempts:
        attempts = login_attempts[test_username]
        print(f"Failed attempts for username: {len(attempts)}")
        for i, attempt in enumerate(attempts, 1):
            print(f"  Attempt {i}: {attempt['timestamp']} - IP: {attempt.get('ip', 'N/A')}")
    
    if test_email in login_attempts:
        attempts = login_attempts[test_email]
        print(f"Failed attempts for email: {len(attempts)}")
    
    # Check locked accounts
    if test_username in locked_accounts:
        lock_until = locked_accounts[test_username]
        remaining = lock_until - datetime.utcnow()
        print(f"Username locked until: {lock_until}")
        print(f"Time remaining: {remaining.total_seconds() / 60:.1f} minutes")
    
    if test_email in locked_accounts:
        lock_until = locked_accounts[test_email]
        remaining = lock_until - datetime.utcnow()
        print(f"Email locked until: {lock_until}")
        print(f"Time remaining: {remaining.total_seconds() / 60:.1f} minutes")
    
    print("\n" + "=" * 50)
    print("🔍 Debug complete. Check server console for real-time debug messages.")

if __name__ == "__main__":
    debug_rate_limiting()
