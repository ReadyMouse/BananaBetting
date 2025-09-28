"""
Test script for creating a new Zcash user account.
Tests the basic flow: create account -> get address -> verify setup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.zcash_mod.zcash_wallet import z_get_new_account, z_getaddressforaccount
from app.zcash_mod.zcash_utils import validate_zcash_address

def test_make_user():
    """Test creating a new Zcash user account and getting their address."""
    print("Testing new user account creation...")
    
    try:
        # Step 1: Create a new account
        print("1. Creating new Zcash account...")
        account_id = z_get_new_account()
        print(f"   ✓ New account created with ID: {account_id}")
        
        # Step 2: Get a unified address for the account
        print("2. Generating unified address for account...")
        unified_address = z_getaddressforaccount(account_id)
        print(f"   ✓ Unified address generated: {unified_address}")
        
        # Step 3: Validate the address
        print("3. Validating the generated address...")
        validation_result = validate_zcash_address(unified_address)
        print(f"   ✓ Address validation result: {validation_result}")
        
        print("\n✅ User account creation test completed successfully!")
        print(f"Account ID: {account_id}")
        print(f"Address: {unified_address}")
        
        return {
            "account_id": account_id,
            "address": unified_address,
            "validation": validation_result
        }
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    result = test_make_user()
