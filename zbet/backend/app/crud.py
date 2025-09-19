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
    
    # Create real Zcash addresses - fail if node is not available
    try:
        zcash_account = zcash_wallet.z_get_new_account()
        zcash_address = zcash_wallet.z_getaddressforaccount(zcash_account)
        zcash_transparent_address = zcash_wallet.z_listunifiedreceivers(zcash_address, 'p2pkh')
        zcash_transparent_balance = str(zcash_wallet.get_transparent_address_balance(zcash_transparent_address))
    except Exception as e:
        from .zcash_mod import ZCASH_RPC_URL
        raise HTTPException(
            status_code=503, 
            detail=f"Failed to connect to Zcash node at {ZCASH_RPC_URL}. "
                   f"Please ensure the Zcash node is running and accessible. "
                   f"Error: {str(e)}"
        )
    
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


def create_sport_event(db: Session, event_data: schemas.SportEventCreate):
    """Create a new sport event"""
    # Convert string datetime to timezone-naive datetime objects
    event_start_time = datetime.fromisoformat(event_data.event_start_time.replace('Z', '+00:00')).replace(tzinfo=None)
    settlement_deadline = datetime.fromisoformat(event_data.settlement_deadline.replace('Z', '+00:00')).replace(tzinfo=None)
    
    db_event = models.SportEvent(
        title=event_data.title,
        description=event_data.description,
        category=models.EventCategory(event_data.category),
        betting_system_type=models.BettingSystemType(event_data.betting_system_type),
        event_start_time=event_start_time,
        settlement_deadline=settlement_deadline,
        status=models.EventStatus.OPEN
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def create_pari_mutuel_event(db: Session, sport_event_id: int, pari_mutuel_data: schemas.PariMutuelEventCreate):
    """Create a pari-mutuel event and its pools"""
    # Create the pari-mutuel event with default settings
    db_pari_event = models.PariMutuelEvent(
        sport_event_id=sport_event_id,
        minimum_bet=0.001,  # Default minimum bet
        maximum_bet=1.0,    # Default maximum bet
        house_fee_percentage=0.05,  # Default 5% house fee
        oracle_fee_percentage=0.02  # Default 2% oracle fee
    )
    
    db.add(db_pari_event)
    db.commit()
    db.refresh(db_pari_event)
    
    # Create the betting pools
    for pool_data in pari_mutuel_data.betting_pools:
        db_pool = models.PariMutuelPool(
            pari_mutuel_event_id=db_pari_event.id,
            outcome_name=pool_data.outcome_name,
            outcome_description=pool_data.outcome_description
        )
        db.add(db_pool)
    
    db.commit()
    return db_pari_event


def get_user_bets(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all bets for a specific user"""
    return db.query(models.Bet).filter(models.Bet.user_id == user_id).offset(skip).limit(limit).all()


def create_bet(db: Session, bet_data: schemas.BetPlacementRequest, user_id: int):
    """Create a new bet record in the database"""
    # Create the bet record
    db_bet = models.Bet(
        user_id=user_id,
        sport_event_id=bet_data.sport_event_id,
        amount=bet_data.amount,
        predicted_outcome=bet_data.predicted_outcome,
        # For now, we'll set deposit status to CONFIRMED for testing
        # In production, this would be PENDING until deposit is confirmed
        deposit_status=models.DepositStatus.CONFIRMED,
        deposit_confirmed_at=datetime.utcnow()
    )
    
    db.add(db_bet)
    db.commit()
    db.refresh(db_bet)
    return db_bet


