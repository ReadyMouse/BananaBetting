#!/usr/bin/env python3
"""
Simple test for address validation specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.zcash_mod.zcash_utils import validate_zcash_address

def test_single_address(address):
    """Test validation of a single address"""
    print(f"🧪 Testing address validation...")
    print(f"   Address: {address}")
    
    try:
        result = validate_zcash_address(address)
        print(f"   ✅ SUCCESS! Address is valid")
        print(f"   📋 Result: {result}")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with a known valid mainnet address
    test_address = "t1MiZLMHUv7XwoJNYQWcCsu8wGtJHeX2Eg9"  # Valid mainnet transparent address
    
    if len(sys.argv) > 1:
        test_address = sys.argv[1]
    
    print("🔍 Simple Address Validation Test")
    print("=" * 40)
    test_single_address(test_address)
    print("=" * 40)
