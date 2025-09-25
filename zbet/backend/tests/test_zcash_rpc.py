#!/usr/bin/env python3
"""
Test for Zcash RPC functionality
Tests the validate_zcash_address function from zcash_utils.py

Usage:
    python test_zcash_rpc.py                                    # Run all tests with default address
    python test_zcash_rpc.py <address>                         # Test specific address
    python test_zcash_rpc.py t1abc123... --connection-only     # Test only connection
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.zcash_mod.zcash_utils import validate_zcash_address
from app.zcash_mod import ZCASH_RPC_URL, ZCASH_RPC_USER, ZCASH_RPC_PASSWORD, DISABLE_ZCASH_NODE
from fastapi import HTTPException

def test_raw_rpc_connection():
    """Test direct RPC connection without using validate_zcash_address"""
    print("🔗 Testing Raw RPC Connection...")
    print(f"   RPC URL: {ZCASH_RPC_URL}")
    print(f"   RPC User: {ZCASH_RPC_USER}")
    print(f"   Disable Node: {DISABLE_ZCASH_NODE}")
    
    # Test basic connectivity
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": "test_connection",
            "method": "getinfo",
            "params": []
        }
        
        print(f"   🔌 Attempting connection to {ZCASH_RPC_URL}...")
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD), timeout=10)
        
        print(f"   📡 Response Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Successfully connected to Zcash node!")
            if 'result' in result:
                print(f"   📋 Node Info: {result['result']}")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Authentication failed - incorrect credentials")
            print(f"   💡 Try updating ZCASH_RPC_USER and ZCASH_RPC_PASSWORD in __init__.py")
            return False
        else:
            print(f"   ❌ Connection failed with status {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print(f"   ❌ Connection timeout - node may be unreachable")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False
    finally:
        print()

def diagnose_connection_issue():
    """Diagnose connection issues with the cherry server"""
    print("🔍 Diagnosing Connection Issue...")
    
    print(f"   Node: Cherry Server Mainnet")
    print(f"   URL: {ZCASH_RPC_URL}")
    print(f"   User: {ZCASH_RPC_USER}")
    print(f"   Password: {'*' * len(ZCASH_RPC_PASSWORD)}")
    
    # Test different authentication approaches
    auth_approaches = [
        ("No Authentication", None),
        ("Empty Credentials", ("", "")),
        ("Current Credentials", (ZCASH_RPC_USER, ZCASH_RPC_PASSWORD)),
        ("Common Defaults", ("zcash", "zcash")),
        ("RPC Defaults", ("rpcuser", "rpcpass")),
    ]
    
    for auth_name, auth_creds in auth_approaches:
        print(f"\n   🔐 Trying: {auth_name}")
        
        try:
            payload = {
                "jsonrpc": "1.0",
                "id": "test_auth",
                "method": "getinfo",
                "params": []
            }
            
            # Make request with or without auth
            if auth_creds is None:
                response = requests.post(ZCASH_RPC_URL, json=payload, timeout=10)
            else:
                response = requests.post(ZCASH_RPC_URL, json=payload, auth=auth_creds, timeout=10)
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ SUCCESS with {auth_name}!")
                if 'result' in result and result['result']:
                    info = result['result']
                    print(f"      📋 Chain: {info.get('chain', 'unknown')}")
                    print(f"      📋 Version: {info.get('version', 'unknown')}")
                    print(f"      📋 Blocks: {info.get('blocks', 'unknown')}")
                
                if auth_creds != (ZCASH_RPC_USER, ZCASH_RPC_PASSWORD):
                    print(f"\n      💡 Update your __init__.py to use:")
                    if auth_creds is None:
                        print(f"         # Remove auth completely, or set to None")
                        print(f"         ZCASH_RPC_USER = None")
                        print(f"         ZCASH_RPC_PASSWORD = None")
                    else:
                        print(f"         ZCASH_RPC_USER = \"{auth_creds[0]}\"")
                        print(f"         ZCASH_RPC_PASSWORD = \"{auth_creds[1]}\"")
                
                return True, auth_creds
            elif response.status_code == 401:
                print(f"      ❌ Authentication failed")
            else:
                print(f"      ❌ Status: {response.status_code}")
                if response.text:
                    print(f"      Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
    
    print(f"\n   💡 All authentication methods failed.")
    print(f"   💡 You may need to:")
    print(f"      1. Check if the node is actually running")
    print(f"      2. SSH to your server and check the zcash.conf file")
    print(f"      3. Look for rpcuser/rpcpassword settings")
    print(f"      4. Check if RPC is enabled and accessible")
    
    return False, None

def test_zcash_rpc_connection():
    """Test basic RPC connection and configuration"""
    print("🔗 Testing Zcash RPC Configuration...")
    print(f"   RPC URL: {ZCASH_RPC_URL}")
    print(f"   RPC User: {ZCASH_RPC_USER}")
    print(f"   Disable Node: {DISABLE_ZCASH_NODE}")
    print()

def test_valid_zcash_address(address=None):
    """Test with a valid Zcash address"""
    print("✅ Testing valid Zcash address validation...")
    
    # Use provided address or default
    if address is None:
        # Default test addresses for different networks
        valid_address = "t1MiZLMHUv7XwoJNYQWcCsu8wGtJHeX2Eg9"  # real mainnet transparent address
    else:
        valid_address = address
    
    print(f"   Testing address: {valid_address}")
    print(f"   Address type: {get_address_type(valid_address)}")
    
    try:
        result = validate_zcash_address(valid_address)
        print(f"   ✅ Address validation successful!")
        print(f"   Result: {result}")
        return True, result
    except HTTPException as e:
        print(f"   ❌ HTTP Exception: {e.detail}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False, None

def get_address_type(address):
    """Determine the type of Zcash address"""
    if address.startswith('t1') or address.startswith('t3'):
        return "Transparent (P2PKH)"
    elif address.startswith('t2'):
        return "Transparent (P2SH)"
    elif address.startswith('zc'):
        return "Sprout Shielded"
    elif address.startswith('zs'):
        return "Sapling Shielded"
    elif address.startswith('u1'):
        return "Unified Address"
    else:
        return "Unknown/Invalid format"

def test_invalid_zcash_address():
    """Test with an invalid Zcash address"""
    print("❌ Testing invalid Zcash address validation...")
    
    invalid_addresses = [
        "invalid_address",
        "t1invalid",
        "zs1invalid", 
        "1234567890",
        "",
        "bitcoin_address_format"
    ]
    
    for invalid_address in invalid_addresses:
        print(f"   Testing invalid address: {invalid_address}")
        try:
            result = validate_zcash_address(invalid_address)
            print(f"   ⚠️  Unexpected success for invalid address: {result}")
        except HTTPException as e:
            print(f"   ✅ Correctly rejected invalid address: {e.detail}")
        except Exception as e:
            print(f"   ⚠️  Unexpected error: {str(e)}")
        print()

def test_rpc_response_structure(address=None):
    """Test the structure of RPC response"""
    print("📋 Testing RPC response structure...")
    
    # Use provided address or default
    test_address = address if address else "t1Hsc1LR8yKnbbe3twRp88p6vFfC5t7DLbs"
    
    try:
        result = validate_zcash_address(test_address)
        print(f"   ✅ Response received successfully!")
        
        # Check expected fields in the response
        expected_fields = ['isvalid', 'address', 'scriptPubKey', 'ismine']
        for field in expected_fields:
            if field in result:
                print(f"   ✅ Field '{field}': {result[field]}")
            else:
                print(f"   ⚠️  Missing expected field: {field}")
        
        # Show all available fields
        print(f"   📋 All response fields: {list(result.keys())}")
        
    except Exception as e:
        print(f"   ❌ Error testing response structure: {str(e)}")

def run_all_tests(test_address=None, connection_only=False):
    """Run all Zcash RPC tests"""
    print("🧪 Starting Zcash RPC Tests")
    print("=" * 50)
    
    # Check if Zcash node is disabled
    if DISABLE_ZCASH_NODE:
        print("⚠️  ZCASH_NODE is DISABLED - tests may not work properly")
        print("   Set DISABLE_ZCASH_NODE = False in __init__.py to enable")
        print()
    
    # Test raw connection first
    print("0️⃣  Testing Raw RPC Connection")
    print("-" * 30)
    connection_works = test_raw_rpc_connection()
    
    # If primary connection fails, diagnose the issue
    if not connection_works:
        print("🔍 Connection failed, running diagnostics...")
        print("-" * 30)
        auth_works, working_creds = diagnose_connection_issue()
        if auth_works:
            print(f"✅ Found working authentication method!")
            connection_works = True
        print()
    
    if connection_only:
        print("🏁 Connection test complete!")
        return
    
    test_zcash_rpc_connection()
    
    print("1️⃣  Testing Valid Address")
    print("-" * 30)
    valid_test_passed, result = test_valid_zcash_address(test_address)
    print()
    
    print("2️⃣  Testing Invalid Addresses") 
    print("-" * 30)
    test_invalid_zcash_address()
    
    if valid_test_passed and result:
        print("3️⃣  Testing Response Structure")
        print("-" * 30)
        test_rpc_response_structure(test_address)
        print()
    
    # Summary
    print("📊 Test Summary")
    print("-" * 30)
    print(f"   🔌 RPC Connection: {'✅ Working' if connection_works else '❌ Failed'}")
    print(f"   ✅ Address Validation: {'✅ Working' if valid_test_passed else '❌ Failed'}")
    
    print("\n🏁 Zcash RPC Tests Complete!")
    print("=" * 50)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Zcash RPC functionality')
    parser.add_argument('address', nargs='?', help='Zcash address to test (optional)')
    parser.add_argument('--connection-only', action='store_true', help='Test only RPC connection')
    
    args = parser.parse_args()
    
    run_all_tests(args.address, args.connection_only)
