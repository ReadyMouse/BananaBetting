#!/usr/bin/env python3
"""
Check Zcash node sync status
"""

import sys
import os
import requests
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.zcash_mod import ZCASH_RPC_URL, ZCASH_RPC_USER, ZCASH_RPC_PASSWORD

def check_node_status():
    """Check the current status of the Zcash node"""
    print("🔍 Checking Zcash Node Status...")
    print(f"   Node: {ZCASH_RPC_URL}")
    
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": "status_check",
            "method": "getinfo",
            "params": []
        }
        
        response = requests.post(
            ZCASH_RPC_URL, 
            json=payload, 
            auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'error' in result and result['error']:
                error = result['error']
                print(f"   ❌ Node Error: {error['message']} (Code: {error['code']})")
                
                if error['code'] == -28:
                    print(f"   🔄 Node is synchronizing - this is normal")
                    print(f"   ⏱️  Please wait for sync to complete")
                    print(f"   💡 You can run this script periodically to check progress")
                    return "syncing"
                else:
                    print(f"   ❌ Unexpected error: {error}")
                    return "error"
            
            elif 'result' in result and result['result']:
                info = result['result']
                print(f"   ✅ Node is ready!")
                print(f"   📊 Blocks: {info.get('blocks', 'unknown')}")
                print(f"   🌐 Connections: {info.get('connections', 'unknown')}")
                print(f"   🔗 Version: {info.get('version', 'unknown')}")
                print(f"   🏠 Network: {'mainnet' if not info.get('testnet', True) else 'testnet'}")
                return "ready"
            
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return "connection_error"
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return "exception"

def main():
    print("🚀 Zcash Node Status Checker")
    print("=" * 40)
    
    status = check_node_status()
    
    print("\n📋 Status Summary:")
    if status == "ready":
        print("   ✅ Node is ready for RPC calls!")
        print("   💡 You can now test address validation")
    elif status == "syncing":
        print("   🔄 Node is still synchronizing")
        print("   ⏱️  Check back in a few minutes")
        print("   📖 This is normal for Zcash nodes")
    else:
        print("   ❌ Node has issues - check connection/credentials")
    
    print("=" * 40)

if __name__ == "__main__":
    main()
