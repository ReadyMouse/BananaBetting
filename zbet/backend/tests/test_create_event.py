#!/usr/bin/env python3
"""
Test script to create a sample SportEvent with pari-mutuel betting
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from ..app.database import engine
from ..app.models import (
    SportEvent, PariMutuelEvent, PariMutuelPool, 
    EventStatus, BettingSystemType, EventCategory
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_event():
    """Create a sample Savannah Bananas betting event"""
    db = SessionLocal()
    try:
        # Create base SportEvent
        sport_event = SportEvent(
            title="Will bananas be thrown onto the field?",
            description="Classic Savannah Bananas tradition - will the crowd toss a banana during tonight's game?",
            category=EventCategory.BANANA_ANTICS,
            status=EventStatus.OPEN,
            betting_system_type=BettingSystemType.PARI_MUTUEL,
            event_start_time=datetime.now() + timedelta(hours=2),
            settlement_deadline=datetime.now() + timedelta(hours=6)
        )
        
        db.add(sport_event)
        db.flush()  # Get the ID without committing
        
        print(f"✅ Created SportEvent: {sport_event.title}")
        print(f"   ID: {sport_event.id}")
        print(f"   Category: {sport_event.category.value}")
        print(f"   System: {sport_event.betting_system_type.value}")
        
        # Create PariMutuelEvent
        pari_event = PariMutuelEvent(
            sport_event_id=sport_event.id,
            minimum_bet=0.001,
            maximum_bet=1.0,
            house_fee_percentage=0.05,
            oracle_fee_percentage=0.02
        )
        
        db.add(pari_event)
        db.flush()
        
        print(f"✅ Created PariMutuelEvent: ID {pari_event.id}")
        print(f"   Min bet: {pari_event.minimum_bet} ZEC")
        print(f"   Max bet: {pari_event.maximum_bet} ZEC")
        print(f"   House fee: {pari_event.house_fee_percentage * 100}%")
        print(f"   Oracle fee: {pari_event.oracle_fee_percentage * 100}%")
        
        # Create betting pools (the possible outcomes)
        pool_yes = PariMutuelPool(
            pari_mutuel_event_id=pari_event.id,
            outcome_name="bananas_thrown",
            outcome_description="Yes, bananas will be thrown onto the field"
        )
        
        pool_no = PariMutuelPool(
            pari_mutuel_event_id=pari_event.id,
            outcome_name="no_bananas",
            outcome_description="No bananas will be thrown onto the field"
        )
        
        db.add_all([pool_yes, pool_no])
        db.commit()
        
        print(f"✅ Created betting pools:")
        print(f"   Pool 1: {pool_yes.outcome_description} (ID: {pool_yes.id})")
        print(f"   Pool 2: {pool_no.outcome_description} (ID: {pool_no.id})")
        
        print(f"\n🎯 Event ready for betting!")
        print(f"   SportEvent ID: {sport_event.id}")
        print(f"   PariMutuelEvent ID: {pari_event.id}")
        
        return sport_event.id, pari_event.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating event: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_event()
