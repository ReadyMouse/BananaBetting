#!/usr/bin/env python3
"""
Direct RPC test to understand the connection issues
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.zcash_mod import ZCASH_RPC_URL, ZCASH_RPC_USER, ZCASH_RPC_PASSWORD

def test_direct_rpc_call(method, params=None):
    """Make a direct RPC call"""
    if params is None:
        params = []
    
    print(f"🔧 Testing RPC method: {method}")
    print(f"   Params: {params}")
    
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": f"test_{method}",
            "method": method,
            "params": params
        }
        
        print(f"   📡 Making request to {ZCASH_RPC_URL}")
        response = requests.post(
            ZCASH_RPC_URL, 
            json=payload, 
            auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD),
            timeout=10
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        print(f"   📄 Full Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'error' in result and result['error']:
                print(f"   ❌ RPC Error Found:")
                error = result['error']
                print(f"      Code: {error.get('code', 'N/A')}")
                print(f"      Message: {error.get('message', 'N/A')}")
                if 'data' in error:
                    print(f"      Data: {error['data']}")
                return False, result
            elif 'result' in result:
                print(f"   ✅ SUCCESS!")
                print(f"   📋 Result: {result['result']}")
                return True, result
            else:
                print(f"   ⚠️  Unexpected response format")
                return False, result
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, None

def main():
    print("🧪 Direct RPC Testing")
    print("=" * 50)
    
    # Test different RPC methods
    methods_to_test = [
        ("getinfo", []),
        ("validateaddress", ["t1MiZLMHUv7XwoJNYQWcCsu8wGtJHeX2Eg9"]),  # Try the non-z version first
        ("z_validateaddress", ["t1MiZLMHUv7XwoJNYQWcCsu8wGtJHeX2Eg9"]),
        ("help", []),  # See what methods are available
    ]
    
    for method, params in methods_to_test:
        print()
        success, result = test_direct_rpc_call(method, params)
        print("-" * 30)
        
        # Don't stop on z_validateaddress failure, try other methods
        if not success and method not in ["z_validateaddress"]:
            print(f"❌ {method} failed - stopping tests")
            break
    
    print("\n🏁 Direct RPC Testing Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
