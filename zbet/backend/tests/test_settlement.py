"""
Test settlement functionality including payout calculation and batch transactions.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app import models, schemas, betting_utils
from app.database import get_db
from app.main import app


# Mock Zcash wallet functions for testing
class MockZcashWallet:
    @staticmethod
    def z_sendmany(from_address: str, recipients: list, minconf: int = 1):
        """Mock z_sendmany that returns a fake operation ID"""
        return "mock_operation_id_12345"


# Patch the zcash_wallet import
import app.betting_utils
app.betting_utils.zcash_wallet = MockZcashWallet


def test_settle_pari_mutuel_event(db_session: Session):
    """Test settling a pari-mutuel event with multiple bets"""
    
    # Create test users
    user1 = models.User(
        username="user1",
        email="user1@test.com",
        hashed_password="hashed_password",
        zcash_address="ztestsapling1user1address",
        zcash_transparent_address="t1user1address",
        zcash_account="0"
    )
    user2 = models.User(
        username="user2", 
        email="user2@test.com",
        hashed_password="hashed_password",
        zcash_address="ztestsapling1user2address",
        zcash_transparent_address="t1user2address",
        zcash_account="1"
    )
    db_session.add_all([user1, user2])
    db_session.commit()
    
    # Create test event
    sport_event = models.SportEvent(
        title="Test Pari-Mutuel Event",
        description="Test event for settlement",
        category=models.EventCategory.BASEBALL,
        status=models.EventStatus.OPEN,
        betting_system_type=models.BettingSystemType.PARI_MUTUEL,
        creator_id=user1.id,
        event_start_time=datetime.utcnow() + timedelta(hours=1),
        event_end_time=datetime.utcnow() + timedelta(hours=3),
        settlement_time=datetime.utcnow() + timedelta(hours=6)
    )
    db_session.add(sport_event)
    db_session.commit()
    
    # Create pari-mutuel event with pools
    pari_event = models.PariMutuelEvent(
        sport_event_id=sport_event.id,
        minimum_bet=0.1,
        maximum_bet=100.0,
        house_fee_percentage=0.05,  # 5%
        creator_fee_percentage=0.02,  # 2%
        validator_fee_percentage=0.02,  # 2%
        total_pool=0.0
    )
    db_session.add(pari_event)
    db_session.commit()
    
    # Create pools
    pool_a = models.PariMutuelPool(
        pari_mutuel_event_id=pari_event.id,
        outcome_name="team_a_wins",
        outcome_description="Team A Wins",
        pool_amount=0.0,
        bet_count=0
    )
    pool_b = models.PariMutuelPool(
        pari_mutuel_event_id=pari_event.id,
        outcome_name="team_b_wins", 
        outcome_description="Team B Wins",
        pool_amount=0.0,
        bet_count=0
    )
    db_session.add_all([pool_a, pool_b])
    db_session.commit()
    
    # Create test bets
    bet1 = models.Bet(
        user_id=user1.id,
        sport_event_id=sport_event.id,
        amount=2.0,
        predicted_outcome="team_a_wins",
        deposit_status=models.DepositStatus.CONFIRMED
    )
    bet2 = models.Bet(
        user_id=user2.id,
        sport_event_id=sport_event.id,
        amount=3.0,
        predicted_outcome="team_b_wins",
        deposit_status=models.DepositStatus.CONFIRMED
    )
    bet3 = models.Bet(
        user_id=user1.id,
        sport_event_id=sport_event.id,
        amount=1.0,
        predicted_outcome="team_a_wins",
        deposit_status=models.DepositStatus.CONFIRMED
    )
    db_session.add_all([bet1, bet2, bet3])
    
    # Update pool amounts manually (normally done by betting_utils.process_bet_placement)
    pool_a.pool_amount = 3.0  # bet1 + bet3
    pool_a.bet_count = 2
    pool_b.pool_amount = 3.0  # bet2
    pool_b.bet_count = 1
    pari_event.total_pool = 6.0
    
    db_session.commit()
    
    # Test settlement with team_a_wins as winner
    house_address = "ztestsapling1houseaddress"
    settlement_response = betting_utils.settle_event(
        db=db_session,
        event_id=sport_event.id,
        winning_outcome="team_a_wins",
        house_address=house_address
    )
    
    # Verify settlement response
    assert settlement_response.event_id == sport_event.id
    assert settlement_response.winning_outcome == "team_a_wins"
    assert settlement_response.total_payouts == 2  # bet1 and bet3
    assert settlement_response.transaction_id == "mock_operation_id_12345"
    
    # Verify event is marked as settled
    db_session.refresh(sport_event)
    assert sport_event.status == models.EventStatus.SETTLED
    assert sport_event.settled_at is not None
    
    # Verify pari-mutuel event has winning outcome
    db_session.refresh(pari_event)
    assert pari_event.winning_outcome == "team_a_wins"
    
    # Verify winning pool is marked
    db_session.refresh(pool_a)
    db_session.refresh(pool_b)
    assert pool_a.is_winning_pool == True
    assert pool_b.is_winning_pool == False
    
    # Verify bet outcomes
    db_session.refresh(bet1)
    db_session.refresh(bet2)
    db_session.refresh(bet3)
    
    assert bet1.outcome == models.BetOutcome.WIN
    assert bet2.outcome == models.BetOutcome.LOSS
    assert bet3.outcome == models.BetOutcome.WIN
    
    # Verify payout amounts (pari-mutuel calculation)
    # Total pool: 6.0, fees: 7% = 0.42, net pool: 5.58
    # Team A pool: 3.0, so each $1 in team A gets 5.58/3.0 = 1.86
    # bet1 (2.0): should get 2.0 * 1.86 = 3.72
    # bet3 (1.0): should get 1.0 * 1.86 = 1.86
    
    expected_bet1_payout = 3.72
    expected_bet3_payout = 1.86
    
    assert abs(bet1.payout_amount - expected_bet1_payout) < 0.01
    assert abs(bet3.payout_amount - expected_bet3_payout) < 0.01
    assert bet2.payout_amount == 0.0
    
    # Verify payout records were created
    payouts = db_session.query(models.Payout).filter(
        models.Payout.sport_event_id == sport_event.id
    ).all()
    
    assert len(payouts) == 2
    assert all(payout.is_processed == True for payout in payouts)
    assert all(payout.zcash_transaction_id == "mock_operation_id_12345" for payout in payouts)


def test_settle_event_validation():
    """Test settlement validation errors"""
    
    # Test with non-existent event
    with pytest.raises(HTTPException) as exc_info:
        betting_utils.settle_event(
            db=db_session,
            event_id=99999,
            winning_outcome="team_a_wins",
            house_address="ztestsapling1house"
        )
    assert exc_info.value.status_code == 404
    assert "Event not found" in str(exc_info.value.detail)


def test_calculate_fees():
    """Test fee calculation for different betting systems"""
    
    # Test pari-mutuel fees (should return 0 as fees are pre-calculated)
    sport_event = models.SportEvent(
        betting_system_type=models.BettingSystemType.PARI_MUTUEL,
        creator_id=1  # Dummy creator_id for test
    )
    pari_event = models.PariMutuelEvent(
        sport_event_id=1,
        house_fee_percentage=0.05,
        creator_fee_percentage=0.02,
        validator_fee_percentage=0.02
    )
    
    # Mock db session that returns pari_event
    class MockDB:
        def query(self, model):
            return MockQuery(pari_event)
    
    class MockQuery:
        def __init__(self, result):
            self.result = result
        def filter(self, *args):
            return self
        def first(self):
            return self.result
    
    mock_db = MockDB()
    house_fee, creator_fee = betting_utils._calculate_fees(mock_db, sport_event, 100.0)
    
    assert house_fee == 0.0
    assert creator_fee == 0.0
    
    # Test fixed odds fees
    sport_event.betting_system_type = models.BettingSystemType.FIXED_ODDS
    house_fee, creator_fee = betting_utils._calculate_fees(mock_db, sport_event, 100.0)
    
    assert house_fee == 2.0  # 2% of 100
    assert creator_fee == 1.0  # 1% of 100


def test_send_batch_payouts():
    """Test batch payout sending with address consolidation"""
    
    # Test with multiple payouts to same address (should consolidate)
    payout_records = [
        schemas.PayoutRecord(
            user_id=1,
            bet_id=1,
            payout_amount=2.5,
            house_fee_deducted=0.1,
            creator_fee_deducted=0.05,
            user_address="ztestsapling1user1address"
        ),
        schemas.PayoutRecord(
            user_id=1,
            bet_id=2,
            payout_amount=1.5,
            house_fee_deducted=0.08,
            creator_fee_deducted=0.04,
            user_address="ztestsapling1user1address"
        ),
        schemas.PayoutRecord(
            user_id=2,
            bet_id=3,
            payout_amount=3.0,
            house_fee_deducted=0.15,
            creator_fee_deducted=0.06,
            user_address="ztestsapling1user2address"
        )
    ]
    
    operation_id = betting_utils._send_batch_payouts("ztestsapling1house", payout_records)
    
    assert operation_id == "mock_operation_id_12345"
    
    # Test with empty payout records
    with pytest.raises(HTTPException) as exc_info:
        betting_utils._send_batch_payouts("ztestsapling1house", [])
    assert exc_info.value.status_code == 400
    assert "No payouts to process" in str(exc_info.value.detail)


if __name__ == "__main__":
    # Simple test runner for development
    print("Running settlement tests...")
    
    # Create in-memory database for testing
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Run tests
    db_session = SessionLocal()
    try:
        test_settle_pari_mutuel_event(db_session)
        print("✓ test_settle_pari_mutuel_event passed")
        
        test_calculate_fees()
        print("✓ test_calculate_fees passed")
        
        test_send_batch_payouts()
        print("✓ test_send_batch_payouts passed")
        
        print("All tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        raise
    finally:
        db_session.close()
