#!/usr/bin/env python3
"""
Integration test demonstrating the complete settlement flow.

This script creates a test event, places bets, and then settles the event
to show the complete payout flow.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models, betting_utils, serializers


def create_test_database():
    """Create an in-memory test database"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def setup_test_data(db):
    """Set up test users, event, and bets"""
    print("Setting up test data...")
    
    # Create test users
    alice = models.User(
        username="alice",
        email="alice@test.com", 
        hashed_password="hashed_password",
        zcash_address="ztestsapling1alice123456789",
        zcash_transparent_address="t1alice123456789",
        zcash_account="0"
    )
    
    bob = models.User(
        username="bob",
        email="bob@test.com",
        hashed_password="hashed_password", 
        zcash_address="ztestsapling1bob123456789",
        zcash_transparent_address="t1bob123456789",
        zcash_account="1"
    )
    
    charlie = models.User(
        username="charlie",
        email="charlie@test.com",
        hashed_password="hashed_password",
        zcash_address="ztestsapling1charlie123456789", 
        zcash_transparent_address="t1charlie123456789",
        zcash_account="2"
    )
    
    db.add_all([alice, bob, charlie])
    db.commit()
    
    # Create a pari-mutuel betting event
    sport_event = models.SportEvent(
        title="Baseball Championship: Giants vs Dodgers",
        description="Final game of the season - winner takes all!",
        category=models.EventCategory.BASEBALL,
        status=models.EventStatus.OPEN,
        betting_system_type=models.BettingSystemType.PARI_MUTUEL,
        creator_id=alice.id,
        event_start_time=datetime.utcnow() + timedelta(hours=2),
        event_end_time=datetime.utcnow() + timedelta(hours=4),
        settlement_time=datetime.utcnow() + timedelta(hours=8)
    )
    db.add(sport_event)
    db.commit()
    
    # Create pari-mutuel event
    pari_event = models.PariMutuelEvent(
        sport_event_id=sport_event.id,
        minimum_bet=0.1,
        maximum_bet=50.0,
        house_fee_percentage=0.05,  # 5% house fee
        creator_fee_percentage=0.02,  # 2% creator fee
        validator_fee_percentage=0.02,  # 2% validator fee
        total_pool=0.0
    )
    db.add(pari_event)
    db.commit()
    
    # Create betting pools
    giants_pool = models.PariMutuelPool(
        pari_mutuel_event_id=pari_event.id,
        outcome_name="giants_win",
        outcome_description="San Francisco Giants Win",
        pool_amount=0.0,
        bet_count=0
    )
    
    dodgers_pool = models.PariMutuelPool(
        pari_mutuel_event_id=pari_event.id,
        outcome_name="dodgers_win", 
        outcome_description="Los Angeles Dodgers Win",
        pool_amount=0.0,
        bet_count=0
    )
    
    db.add_all([giants_pool, dodgers_pool])
    db.commit()
    
    # Place some bets
    print("Placing bets...")
    
    # Alice bets 5 ZEC on Giants
    alice_bet = models.Bet(
        user_id=alice.id,
        sport_event_id=sport_event.id,
        amount=5.0,
        predicted_outcome="giants_win",
        deposit_status=models.DepositStatus.CONFIRMED,
        deposit_confirmed_at=datetime.utcnow()
    )
    
    # Bob bets 10 ZEC on Dodgers  
    bob_bet = models.Bet(
        user_id=bob.id,
        sport_event_id=sport_event.id,
        amount=10.0,
        predicted_outcome="dodgers_win",
        deposit_status=models.DepositStatus.CONFIRMED,
        deposit_confirmed_at=datetime.utcnow()
    )
    
    # Charlie bets 2 ZEC on Giants
    charlie_bet = models.Bet(
        user_id=charlie.id,
        sport_event_id=sport_event.id,
        amount=2.0,
        predicted_outcome="giants_win", 
        deposit_status=models.DepositStatus.CONFIRMED,
        deposit_confirmed_at=datetime.utcnow()
    )
    
    db.add_all([alice_bet, bob_bet, charlie_bet])
    
    # Update pool statistics (normally done by betting_utils.process_bet_placement)
    giants_pool.pool_amount = 7.0  # Alice (5) + Charlie (2)
    giants_pool.bet_count = 2
    dodgers_pool.pool_amount = 10.0  # Bob (10)
    dodgers_pool.bet_count = 1
    pari_event.total_pool = 17.0  # Total of all bets
    
    db.commit()
    
    print(f"Event created: {sport_event.title}")
    print(f"Total pool: {pari_event.total_pool} ZEC")
    print(f"Giants pool: {giants_pool.pool_amount} ZEC ({giants_pool.bet_count} bets)")
    print(f"Dodgers pool: {dodgers_pool.pool_amount} ZEC ({dodgers_pool.bet_count} bets)")
    print()
    
    return sport_event, [alice, bob, charlie], [alice_bet, bob_bet, charlie_bet]


def demonstrate_payout_calculation(db, sport_event, users, bets):
    """Show potential payouts before settlement"""
    print("=== POTENTIAL PAYOUTS (before settlement) ===")
    
    for bet in bets:
        user = next(u for u in users if u.id == bet.user_id)
        potential_payout = serializers._calculate_potential_payout(bet, sport_event, db)
        
        print(f"{user.username}: {bet.amount} ZEC on '{bet.predicted_outcome}' → "
              f"potential payout: {potential_payout:.3f} ZEC")
    print()


def settle_event_and_show_results(db, sport_event):
    """Settle the event and show the final results"""
    print("=== SETTLING EVENT ===")
    print("Final outcome: Giants Win! 🎉")
    print()
    
    # Mock the zcash wallet for this test
    class MockZcashWallet:
        @staticmethod
        def z_sendmany(from_address, recipients, minconf=1):
            print(f"Sending batch transaction from {from_address}:")
            total_amount = 0
            for recipient in recipients:
                print(f"  → {recipient['amount']:.4f} ZEC to {recipient['address']}")
                total_amount += recipient['amount']
            print(f"Total payout: {total_amount:.4f} ZEC")
            print()
            return "opid-12345-test-transaction"
    
    # Patch the wallet
    original_wallet = betting_utils.zcash_wallet
    betting_utils.zcash_wallet = MockZcashWallet()
    
    try:
        # Settle the event
        house_address = "ztestsapling1house123456789"
        settlement_response = betting_utils.settle_event(
            db=db,
            event_id=sport_event.id,
            winning_outcome="giants_win",
            house_address=house_address
        )
        
        print("=== SETTLEMENT RESULTS ===")
        print(f"Event ID: {settlement_response.event_id}")
        print(f"Winning outcome: {settlement_response.winning_outcome}")
        print(f"Total payouts: {settlement_response.total_payouts}")
        print(f"Total payout amount: {settlement_response.total_payout_amount:.4f} ZEC")
        print(f"Transaction ID: {settlement_response.transaction_id}")
        print()
        
        print("=== INDIVIDUAL PAYOUTS ===")
        for payout in settlement_response.payout_records:
            user = db.query(models.User).filter(models.User.id == payout.user_id).first()
            bet = db.query(models.Bet).filter(models.Bet.id == payout.bet_id).first()
            
            gross_payout = payout.payout_amount + payout.house_fee_deducted + payout.creator_fee_deducted
            
            print(f"{user.username}: {bet.amount} ZEC bet → {payout.payout_amount:.4f} ZEC payout")
            print(f"  Gross payout: {gross_payout:.4f} ZEC")
            print(f"  House fee: {payout.house_fee_deducted:.4f} ZEC")
            print(f"  Creator fee: {payout.creator_fee_deducted:.4f} ZEC")
            print(f"  Net payout: {payout.payout_amount:.4f} ZEC")
            print(f"  Address: {payout.user_address}")
            print()
            
    finally:
        # Restore original wallet
        betting_utils.zcash_wallet = original_wallet


def show_payout_calculation_details(db, sport_event):
    """Show detailed payout calculation explanation"""
    print("=== PAYOUT CALCULATION EXPLANATION ===")
    
    # Get pari-mutuel event details
    pari_event = db.query(models.PariMutuelEvent).filter(
        models.PariMutuelEvent.sport_event_id == sport_event.id
    ).first()
    
    giants_pool = db.query(models.PariMutuelPool).filter(
        models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
        models.PariMutuelPool.outcome_name == "giants_win"
    ).first()
    
    print(f"Total pool: {pari_event.total_pool} ZEC")
    print(f"House fee: {pari_event.house_fee_percentage * 100}%")
    print(f"Creator fee: {pari_event.creator_fee_percentage * 100}%")
    print(f"Total fees: {(pari_event.house_fee_percentage + pari_event.creator_fee_percentage) * 100}%")
    print()
    
    total_fees = pari_event.total_pool * (pari_event.house_fee_percentage + pari_event.creator_fee_percentage)
    net_pool = pari_event.total_pool - total_fees
    
    print(f"Fee amount: {total_fees:.4f} ZEC")
    print(f"Net prize pool: {net_pool:.4f} ZEC")
    print(f"Winning pool (Giants): {giants_pool.pool_amount} ZEC")
    print()
    
    losing_pool_total = pari_event.total_pool - giants_pool.pool_amount
    
    print("Payout formula: Original Bet + (Individual Bet / Winning Pool) × Losing Pools - Fees")
    print(f"Losing pool total: {losing_pool_total:.4f} ZEC")
    print(f"Alice (5 ZEC): 5 + (5 / {giants_pool.pool_amount}) × {losing_pool_total:.4f} - fees = {5 + (5 / giants_pool.pool_amount) * losing_pool_total:.4f} ZEC (before fees)")
    print(f"Charlie (2 ZEC): 2 + (2 / {giants_pool.pool_amount}) × {losing_pool_total:.4f} - fees = {2 + (2 / giants_pool.pool_amount) * losing_pool_total:.4f} ZEC (before fees)")
    print()


def main():
    """Run the complete settlement demonstration"""
    print("🎲 Banana Betting Settlement System Demo 🎲")
    print("=" * 50)
    print()
    
    # Create test database
    db = create_test_database()
    
    try:
        # Set up test data
        sport_event, users, bets = setup_test_data(db)
        
        # Show potential payouts
        demonstrate_payout_calculation(db, sport_event, users, bets)
        
        # Show detailed calculation
        show_payout_calculation_details(db, sport_event)
        
        # Settle event and show results
        settle_event_and_show_results(db, sport_event)
        
        print("✅ Settlement demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during settlement: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
