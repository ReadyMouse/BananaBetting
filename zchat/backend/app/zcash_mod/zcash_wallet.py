import requests
from fastapi import Depends, FastAPI, HTTPException, status, Query
from ..zcash_mod import ZCASH_RPC_URL, ZCASH_RPC_USER,ZCASH_RPC_PASSWORD

def backupwallet(destination: str):
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "backupwallet",
            "method": "backupwallet",
            "params": [destination]
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        print(validation_data)
        return validation_data['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def z_get_new_account():
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "z_getnewaccount",
            "method": "z_getnewaccount",
            "params": []
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        return validation_data['result']['account']
    
    except Exception as e:
        print('Here')
        raise HTTPException(status_code=500, detail=str(e))


def z_listunifiedreceivers(address: str, acc_type: str):
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "z_listunifiedreceivers",
            "method": "z_listunifiedreceivers",
            "params": [address]
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        return validation_data['result'][acc_type]
    
    except Exception as e:
        print('Here')
        raise HTTPException(status_code=500, detail=str(e))


def get_transparent_address_balance(address: str):
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "getaddressbalance",
            "method": "getaddressbalance",
            "params": [{ "addresses": [address,] }]
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        return validation_data['result']['balance']
    
    except Exception as e:
        print('Here')
        raise HTTPException(status_code=500, detail=str(e))

def z_getaddressforaccount(account: int, receiver_type=None, diversifier_index: int=None):
    params = [account]
    if receiver_type is not None:
        params.append(receiver_type)
    if diversifier_index is not None:
        params.append(diversifier_index)
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "z_getaddressforaccount",
            "method": "z_getaddressforaccount",
            "params": params
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        return validation_data['result']['address']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def send_to_address(address: str, amount: float|int, comment: str=None, comment_to: str=None, subtractfeefromamount: bool=False):
    try:
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "sendtoaddress",
            "method": "sendtoaddress",
            "params": [address, amount, comment, comment_to, subtractfeefromamount]
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        validation_data = response.json()
        return validation_data['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# UNTESTED
def z_sendmany(from_address: str, recipients: list, minconf: int = 1, fee: float = None, privacy_policy: str = None):
    """
    Send ZEC to multiple addresses in a single transaction using z_sendmany RPC
    Based on official Zcash RPC documentation: https://zcash.github.io/rpc/z_sendmany.html
    
    Args:
        from_address: The address to send from (string, not account number)
        recipients: List of {"address": "zaddr", "amount": 0.01} dictionaries
        minconf: Minimum confirmations for inputs (default: 1)
        fee: Transaction fee (optional)
        privacy_policy: Privacy policy for the transaction (optional)
    
    Returns:
        Operation ID for tracking the async transaction
    """
    try:
        # Validate recipients format and check for duplicates
        amounts_array = []
        seen_addresses = set()
        
        for recipient in recipients:
            if not isinstance(recipient, dict) or "address" not in recipient or "amount" not in recipient:
                raise HTTPException(
                    status_code=400, 
                    detail="Recipients must be list of {'address': 'addr', 'amount': 0.01} objects"
                )
            
            address = recipient["address"]
            amount = recipient["amount"]
            
            # Check for duplicate addresses (Zcash limitation)
            if address in seen_addresses:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Duplicate address in recipients: {address}. Zcash doesn't allow multiple outputs to same address."
                )
            seen_addresses.add(address)
            
            amounts_array.append({"address": address, "amount": amount})
        
        # Build parameters according to official z_sendmany format
        params = [from_address, amounts_array]
        if minconf is not None:
            params.append(minconf)
        if fee is not None:
            params.append(fee)
        if privacy_policy is not None:
            params.append(privacy_policy)
        
        # RPC request payload
        payload = {
            "jsonrpc": "1.0",
            "id": "z_sendmany",
            "method": "z_sendmany",
            "params": params
        }
        
        # Make the request to the Zcash node
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        # Handle Zcash node response
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        # Parse response
        result = response.json()
        if 'error' in result and result['error']:
            raise HTTPException(status_code=500, detail=f"Zcash error: {result['error']}")
            
        return result['result']  # Returns operation ID for async operation
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def z_getoperationstatus(operation_ids: list = None):
    """
    Get status of z_sendmany operations
    
    Args:
        operation_ids: List of operation IDs to check, or None for all
    
    Returns:
        List of operation status objects
    """
    try:
        params = []
        if operation_ids:
            params.append(operation_ids)
        
        payload = {
            "jsonrpc": "1.0",
            "id": "z_getoperationstatus",
            "method": "z_getoperationstatus",
            "params": params
        }
        
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        result = response.json()
        return result['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))