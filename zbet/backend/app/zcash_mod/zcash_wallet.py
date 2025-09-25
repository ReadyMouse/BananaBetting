import requests
from fastapi import Depends, FastAPI, HTTPException, status, Query
from ..zcash_mod import ZCASH_RPC_URL, ZCASH_RPC_USER, ZCASH_RPC_PASSWORD, DISABLE_ZCASH_NODE

# Mock balances for development (user_id -> balance)
_mock_user_balances = {}
_mock_pool_balance = 1000.0

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
    """Get transparent address balance. Uses mock data in dev mode."""
    if DISABLE_ZCASH_NODE:
        # For development, return mock balance based on address
        # Extract user_id from address if it's a user address, else return pool balance
        return _mock_user_balances.get(address, 10.0)  # Default 10 ZEC for users
    
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


def z_getbalance(account: int = None, minconf: int = 1, include_watchonly: bool = False):
    """
    Get the shielded balance for an account.
    This is used to check shielded ZEC balances.
    
    Args:
        account: Account number (None for all accounts)
        minconf: Minimum confirmations required (default: 1)
        include_watchonly: Include watch-only addresses
    
    Returns:
        Shielded balance amount
    """
    if DISABLE_ZCASH_NODE:
        # Return mock pool balance for dev mode
        return _mock_pool_balance
    
    try:
        params = []
        if account is not None:
            params.append(account)
            if minconf != 1:
                params.append(minconf)
                if include_watchonly:
                    params.append(include_watchonly)
        
        payload = {
            "jsonrpc": "1.0",
            "id": "z_getbalance",
            "method": "z_getbalance",
            "params": params
        }
        
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        result = response.json()
        return float(result['result'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def z_listreceivedbyaddress(address: str, minconf: int = 1):
    """
    List amounts received by a specific shielded address.
    This is used to verify shielded deposits for betting.
    
    Args:
        address: The shielded address to check
        minconf: Minimum confirmations required (default: 1)
    
    Returns:
        List of received amounts and transaction details
    """
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": "z_listreceivedbyaddress",
            "method": "z_listreceivedbyaddress",
            "params": [address, minconf]
        }
        
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        result = response.json()
        return result['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def list_transactions(account: str = "*", count: int = 10, skip: int = 0):
    """
    List recent transactions for an account or all accounts.
    Used to find specific deposit transactions.
    
    Args:
        account: Account name or "*" for all accounts
        count: Number of transactions to return
        skip: Number of transactions to skip
    
    Returns:
        List of transaction objects
    """
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": "listtransactions",
            "method": "listtransactions",
            "params": [account, count, skip]
        }
        
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        result = response.json()
        return result['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_transaction(txid: str):
    """
    Get detailed information about a specific transaction.
    
    Args:
        txid: Transaction ID to look up
    
    Returns:
        Transaction details including confirmations
    """
    try:
        payload = {
            "jsonrpc": "1.0",
            "id": "gettransaction",
            "method": "gettransaction",
            "params": [txid]
        }
        
        response = requests.post(ZCASH_RPC_URL, json=payload, auth=(ZCASH_RPC_USER, ZCASH_RPC_PASSWORD))
        
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=500, detail="Failed to connect to Zcash node")

        result = response.json()
        return result['result']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def verify_shielded_deposit(address: str, expected_amount: float, min_confirmations: int = 6):
    """
    Verify that a shielded deposit of the expected amount has been received at an address.
    This is the main function for confirming shielded bet deposits.
    
    Args:
        address: The shielded address to check for deposits
        expected_amount: The amount we expect to receive
        min_confirmations: Minimum confirmations required
    
    Returns:
        Dict with verification status and details
    """
    try:
        # Get transactions received with minimum confirmations
        confirmed_txs = z_listreceivedbyaddress(address, min_confirmations)
        
        # Get all transactions (including unconfirmed)
        all_txs = z_listreceivedbyaddress(address, 0)
        
        # Calculate total amounts
        confirmed_amount = sum(float(tx.get('amount', 0)) for tx in confirmed_txs)
        total_amount = sum(float(tx.get('amount', 0)) for tx in all_txs)
        
        # Check if we have enough confirmed funds
        if confirmed_amount >= expected_amount:
            return {
                "status": "confirmed",
                "confirmed_amount": confirmed_amount,
                "total_amount": total_amount,
                "confirmations": min_confirmations,
                "transactions": confirmed_txs,
                "message": f"Shielded deposit confirmed: {confirmed_amount} ZEC received"
            }
        
        # Check if we have unconfirmed funds
        elif total_amount >= expected_amount:
            pending_amount = total_amount - confirmed_amount
            return {
                "status": "pending",
                "confirmed_amount": confirmed_amount,
                "total_amount": total_amount,
                "pending_amount": pending_amount,
                "confirmations": 0,
                "transactions": all_txs,
                "message": f"Shielded deposit pending confirmation: {total_amount} ZEC received, {pending_amount} ZEC awaiting {min_confirmations} confirmations"
            }
        
        # Not enough funds received
        else:
            return {
                "status": "insufficient", 
                "confirmed_amount": confirmed_amount,
                "total_amount": total_amount,
                "expected_amount": expected_amount,
                "transactions": all_txs,
                "message": f"Insufficient shielded funds: expected {expected_amount} ZEC, received {total_amount} ZEC"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error checking shielded deposit: {str(e)}"
        }


# Helper functions for development mode balance management
def get_user_balance_by_address(address: str) -> float:
    """Get user balance by their Zcash address."""
    if DISABLE_ZCASH_NODE:
        return _mock_user_balances.get(address, 10.0)
    else:
        return get_transparent_address_balance(address)

def deduct_user_balance(address: str, amount: float) -> None:
    """Deduct amount from user's balance (dev mode only)."""
    if DISABLE_ZCASH_NODE:
        current = _mock_user_balances.get(address, 10.0)
        _mock_user_balances[address] = max(0, current - amount)

def add_user_balance(address: str, amount: float) -> None:
    """Add amount to user's balance (dev mode only)."""
    if DISABLE_ZCASH_NODE:
        current = _mock_user_balances.get(address, 10.0)
        _mock_user_balances[address] = current + amount

def get_pool_balance() -> float:
    """Get pool balance."""
    if DISABLE_ZCASH_NODE:
        return _mock_pool_balance
    else:
        # In production, would check actual pool address
        from ..config import settings
        pool_address = settings.get_pool_address()
        try:
            return get_transparent_address_balance(pool_address)
        except:
            # Try shielded if transparent fails
            return z_getbalance()