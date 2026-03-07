"""
Fix duplicate PayPal endpoints by truncating the file
"""

# Read the original file with UTF-8 encoding
with open("api/v1/payments.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Keep only lines up to line 614 (before the duplicates)
fixed_lines = lines[:614]

# Write the fixed version with UTF-8 encoding
with open("api/v1/payments.py", "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print(f"✅ Fixed payments.py - removed duplicate endpoints")
print(f"✅ Original file had {len(lines)} lines")
print(f"✅ Fixed file has {len(fixed_lines)} lines")
print(f"✅ Removed {len(lines) - len(fixed_lines)} lines of duplicates")
