from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import json

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    zcash_account = Column(String, primary_key=False)
    zcash_address = Column(String, unique=True, index=True)
    zcash_transparent_address = Column(String, unique=True, index=True)
    balance = Column(String, unique=False, index=True)

    # Relationships
    bets = relationship("Bet", back_populates="user")
    payouts = relationship("Payout", back_populates="user")


# Enums for status fields
class EventStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed" 
    SETTLED = "settled"
    CANCELLED = "cancelled"


class BetOutcome(enum.Enum):
    WIN = "win"
    LOSS = "loss"
    PUSH = "push" # neither win or lose, stalemate, tie, etc. 


class EventCategory(enum.Enum):
    BASEBALL = "baseball"
    BANANA_ANTICS = "banana-antics"
    CROWD_FUN = "crowd-fun"
    PLAYER_PROPS = "player-props"


class BettingSystemType(enum.Enum):
    PARI_MUTUEL = "pari_mutuel"
    # TODO: implement fixed odds and spread systems 
    FIXED_ODDS = "fixed_odds"
    SPREAD = "spread"


# Base SportEvent model
class SportEvent(Base):
    __tablename__ = "sport_events"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(EventCategory), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.OPEN, nullable=False)
    betting_system_type = Column(Enum(BettingSystemType), nullable=False)
    
    # Event timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_start_time = Column(DateTime, nullable=False)
    settlement_deadline = Column(DateTime, nullable=False)
    settled_at = Column(DateTime, nullable=True)
    
    # Serialization methods
    def to_dict(self, db_session):
        """Convert to dictionary with all related data"""
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "betting_system_type": self.betting_system_type.value,
            "created_at": self.created_at.isoformat(),
            "event_start_time": self.event_start_time.isoformat(),
            "settlement_deadline": self.settlement_deadline.isoformat(),
            "settled_at": self.settled_at.isoformat() if self.settled_at else None
        }
        
        # Each betting system handles its own data
        if self.betting_system_type == BettingSystemType.PARI_MUTUEL:
            pari_event = db_session.query(PariMutuelEvent).filter_by(sport_event_id=self.id).first()
            if pari_event:
                data["betting_system_data"] = pari_event.to_dict(db_session)
        
        return data


# Pari-Mutuel specific betting structure
class PariMutuelEvent(Base):
    __tablename__ = "pari_mutuel_events"

    id = Column(Integer, primary_key=True)
    sport_event_id = Column(Integer, ForeignKey("sport_events.id"), nullable=False)
    
    # Pari-mutuel specific fields
    total_pool = Column(Float, default=0.0, nullable=False)  # Total amount bet across all outcomes
    winning_outcome = Column(String(50), nullable=True)  # The actual winning outcome
    
    # Pari-mutuel betting parameters
    minimum_bet = Column(Float, nullable=False, default=0.001)
    maximum_bet = Column(Float, nullable=False, default=1.0)
    house_fee_percentage = Column(Float, default=0.05, nullable=False)  # 5% default house fee
    oracle_fee_percentage = Column(Float, default=0.02, nullable=False)  # 2% default oracle fee
    
    # Relationships
    betting_pools = relationship("PariMutuelPool", back_populates="pari_mutuel_event")
    
    # Utility methods
    def get_bets(self, db_session):
        """Get all bets for this pari-mutuel event"""
        return db_session.query(Bet).filter(
            Bet.sport_event_id == self.sport_event_id,
            Bet.betting_metadata.contains(f'"pari_mutuel_event_id": {self.id}')
        ).all()
    
    def to_dict(self, db_session):
        """Convert to dictionary with all related data"""
        pools = db_session.query(PariMutuelPool).filter_by(pari_mutuel_event_id=self.id).all()
        
        return {
            "id": self.id,
            "minimum_bet": self.minimum_bet,
            "maximum_bet": self.maximum_bet,
            "house_fee_percentage": self.house_fee_percentage,
            "oracle_fee_percentage": self.oracle_fee_percentage,
            "total_pool": self.total_pool,
            "winning_outcome": self.winning_outcome,
            "betting_pools": [pool.to_dict() for pool in pools]
        }


# Individual betting pools for each possible outcome in pari-mutuel
class PariMutuelPool(Base):
    __tablename__ = "pari_mutuel_pools"

    id = Column(Integer, primary_key=True)
    pari_mutuel_event_id = Column(Integer, ForeignKey("pari_mutuel_events.id"), nullable=False)
    
    # Pool details
    outcome_name = Column(String(50), nullable=False)  # "team_a_wins", "over_5_goals", etc.
    outcome_description = Column(String(255), nullable=False)  # Human readable description
    pool_amount = Column(Float, default=0.0, nullable=False)  # Total amount bet on this outcome
    bet_count = Column(Integer, default=0, nullable=False)  # Number of bets on this outcome
    
    # Payout calculation (set when event settles)
    payout_ratio = Column(Float, nullable=True)  # How much each dollar wins (after fees)
    is_winning_pool = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    pari_mutuel_event = relationship("PariMutuelEvent", back_populates="betting_pools")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "outcome_name": self.outcome_name,
            "outcome_description": self.outcome_description,
            "pool_amount": self.pool_amount,
            "bet_count": self.bet_count,
            "payout_ratio": self.payout_ratio,
            "is_winning_pool": self.is_winning_pool
        }


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sport_event_id = Column(Integer, ForeignKey("sport_events.id"), nullable=False)
    
    # Bet details - system agnostic
    amount = Column(Float, nullable=False)  # Amount in ZEC
    predicted_outcome = Column(String(50), nullable=False)  # The outcome identifier they're betting on
    outcome = Column(Enum(BetOutcome), nullable=True)  # Set when event is settled (WIN/LOSS/PUSH)
    
    # System-agnostic betting metadata (JSON field for flexibility)
    betting_metadata = Column(Text, nullable=True)  # JSON string for system-specific data
    
    # Transaction details
    zcash_transaction_id = Column(String(100), nullable=True)  # Transaction hash for placing bet
    bet_placed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Payout details (calculated when event settles)
    payout_amount = Column(Float, nullable=True)  # Final payout amount after settlement
    house_fee_deducted = Column(Float, nullable=True)  # House fee deducted from this bet
    oracle_fee_deducted = Column(Float, nullable=True)  # Oracle fee deducted from this bet
    
    # Relationships
    user = relationship("User", back_populates="bets")
    sport_event = relationship("SportEvent")  # No back_populates since SportEvent doesn't manage bets
    payout = relationship("Payout", back_populates="bet", uselist=False)
    
    # Utility methods for betting metadata
    def get_betting_metadata(self):
        """Parse betting_metadata JSON field"""
        if self.betting_metadata:
            return json.loads(self.betting_metadata)
        return {}
    
    def set_betting_metadata(self, metadata_dict):
        """Set betting_metadata from dictionary"""
        self.betting_metadata = json.dumps(metadata_dict)
    
    def get_pari_mutuel_pool_id(self):
        """Helper to get pari-mutuel pool ID from metadata"""
        metadata = self.get_betting_metadata()
        return metadata.get('pari_mutuel_pool_id')
    
    def set_pari_mutuel_pool_id(self, pool_id):
        """Helper to set pari-mutuel pool ID in metadata"""
        metadata = self.get_betting_metadata()
        metadata['pari_mutuel_pool_id'] = pool_id
        self.set_betting_metadata(metadata)


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bet_id = Column(Integer, ForeignKey("bets.id"), nullable=False)
    sport_event_id = Column(Integer, ForeignKey("sport_events.id"), nullable=False)
    
    # Payout details
    payout_amount = Column(Float, nullable=False)  # Amount in ZEC
    house_fee_deducted = Column(Float, nullable=False)  # House fee amount deducted
    oracle_fee_deducted = Column(Float, nullable=False, default=0.0)  # Oracle/settlement fee deducted
    
    # Transaction details
    zcash_transaction_id = Column(String(100), nullable=True)  # Payout transaction hash
    payout_processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_processed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payouts")
    bet = relationship("Bet", back_populates="payout")
    sport_event = relationship("SportEvent")

