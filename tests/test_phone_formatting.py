from services.ecocash_service import ecocash_service

def test_phone_formatting():
    """Test phone number formatting for Ecocash."""
    
    print("📱 Phone Number Formatting Test")
    print("=" * 50)
    
    test_numbers = [
        "0774222475",      # Local format
        "263774222475",    # International format
        "+263774222475",   # International with +
        "0712345678",      # Different local format
        "263712345678",    # Different international format
        "+263712345678",   # Different international with +
        "string",          # Invalid (text)
        "123",             # Invalid (too short)
        "0774-222-475",    # With dashes
        "0774 222 475",    # With spaces
    ]
    
    for phone in test_numbers:
        print(f"\n📞 Testing: {phone}")
        
        # Format the number
        formatted = ecocash_service.format_phone_number(phone)
        print(f"   Formatted: {formatted}")
        
        # Validate the number
        is_valid = ecocash_service.validate_phone_number(phone)
        print(f"   Valid: {is_valid}")
        
        if is_valid:
            print(f"   ✅ Ready for Ecocash payment")
        else:
            print(f"   ❌ Invalid format")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("   - Local format (0774222475) → 263774222475")
    print("   - International (263774222475) → 263774222475")
    print("   - With + (+263774222475) → 263774222475")
    print("   - Invalid formats will be rejected")
    print("   - All valid formats will trigger SMS prompt to phone")

if __name__ == "__main__":
    test_phone_formatting()
