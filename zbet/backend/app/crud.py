from fastapi import HTTPException
from datetime import datetime

from sqlalchemy.orm import Session

from . import auth, models, schemas, cleaners
from .zcash_mod import zcash_utils, zcash_wallet


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_zcash_address(db: Session, zcash_address: str):
    return db.query(models.User).filter(models.User.zcash_address == zcash_address).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_some_users(db: Session, current_user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.id != current_user_id).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    # cleaners.validate_eth_address(user.wallet_address)
    # zcash_utils.validate_zcash_address(user.wallet_address)
    # zcash_utils.validate_zcash_address('address')
    # zcash_wallet.send_to_address('address', 0.1)
    
    # Development mode: Create mock Zcash data when node is not available
    try:
        zcash_account = zcash_wallet.z_get_new_account()
        zcash_address = zcash_wallet.z_getaddressforaccount(zcash_account)
        zcash_transparent_address = zcash_wallet.z_listunifiedreceivers(zcash_address, 'p2pkh')
        zcash_transparent_balance = str(zcash_wallet.get_transparent_address_balance(zcash_transparent_address))
    except Exception as e:
        # Fallback for development when Zcash node is not running
        import uuid
        from .zcash_mod import USE_TESTNET
        
        # Generate more realistic-looking mock addresses
        random_suffix = uuid.uuid4().hex
        zcash_account = f"dev_account_{random_suffix[:8]}"
        
        if USE_TESTNET:
            # Testnet address format (more realistic length)
            zcash_address = f"ztestsapling1{random_suffix[:50]}"
            zcash_transparent_address = f"tm{random_suffix[:32]}"
        else:
            # Mainnet address format (more realistic length)  
            zcash_address = f"zs1{random_suffix[:75]}"
            zcash_transparent_address = f"t1{random_suffix[:32]}"
            
        zcash_transparent_balance = "0.0"
        print(f"Warning: Using mock Zcash data for development ({('testnet' if USE_TESTNET else 'mainnet')}) - {str(e)}")
    
    db_user = models.User(email=user.email.lower(), username=user.username.lower(), zcash_account=zcash_account, zcash_address=zcash_address, zcash_transparent_address=zcash_transparent_address, hashed_password=hashed_password, balance=zcash_transparent_balance)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Betting CRUD functions
def get_sport_events(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    """Get all sport events with optional status filter"""
    query = db.query(models.SportEvent)
    if status:
        query = query.filter(models.SportEvent.status == status)
    return query.offset(skip).limit(limit).all()


def get_sport_event(db: Session, event_id: int):
    """Get a single sport event by ID"""
    return db.query(models.SportEvent).filter(models.SportEvent.id == event_id).first()



