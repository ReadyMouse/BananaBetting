#!/usr/bin/env python3
"""
Script to view created events and their details
"""

from sqlalchemy.orm import sessionmaker
from ..app.database import engine
from ..app.models import (
    SportEvent, PariMutuelEvent, PariMutuelPool
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def view_all_events():
    """View all SportEvents and their details"""
    db = SessionLocal()
    try:
        events = db.query(SportEvent).all()
        
        if not events:
            print("📭 No events found in database")
            return
            
        print(f"📋 Found {len(events)} event(s):\n")
        
        for event in events:
            print(f"🎯 SportEvent #{event.id}")
            print(f"   Title: {event.title}")
            print(f"   Description: {event.description}")
            print(f"   Category: {event.category.value}")
            print(f"   Status: {event.status.value}")
            print(f"   Betting System: {event.betting_system_type.value}")
            print(f"   Event Start: {event.event_start_time}")
            print(f"   Settlement Deadline: {event.settlement_deadline}")
            
            # If it's a pari-mutuel event, show details
            if event.betting_system_type.value == "pari_mutuel":
                pari_event = db.query(PariMutuelEvent).filter_by(sport_event_id=event.id).first()
                if pari_event:
                    print(f"\n   💰 Pari-Mutuel Details:")
                    print(f"      Min Bet: {pari_event.minimum_bet} ZEC")
                    print(f"      Max Bet: {pari_event.maximum_bet} ZEC")
                    print(f"      House Fee: {pari_event.house_fee_percentage * 100}%")
                    print(f"      Creator Fee: {pari_event.creator_fee_percentage * 100}%")
                    print(f"      Total Pool: {pari_event.total_pool} ZEC")
                    
                    # Show betting pools
                    pools = db.query(PariMutuelPool).filter_by(pari_mutuel_event_id=pari_event.id).all()
                    if pools:
                        print(f"\n   🎲 Betting Pools:")
                        for pool in pools:
                            print(f"      Pool #{pool.id}: {pool.outcome_description}")
                            print(f"         Outcome: {pool.outcome_name}")
                            print(f"         Pool Amount: {pool.pool_amount} ZEC")
                            print(f"         Bet Count: {pool.bet_count}")
                            if pool.is_winning_pool:
                                print(f"         🏆 WINNING POOL")
            
            print(f"\n" + "="*60 + "\n")
            
    except Exception as e:
        print(f"❌ Error viewing events: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    view_all_events()
