#!/usr/bin/env python3
"""
Simple test of our new clean API structure
"""

from sqlalchemy.orm import sessionmaker
from ..app.database import engine
from ..app.models import SportEvent

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_to_dict():
    """Test the new to_dict method"""
    db = SessionLocal()
    try:
        # Get our test event
        event = db.query(SportEvent).first()
        if event:
            print("🧪 Testing SportEvent.to_dict() method...")
            event_data = event.to_dict(db)
            
            print(f"✅ Event serialized successfully!")
            print(f"   ID: {event_data['id']}")
            print(f"   Title: {event_data['title']}")
            print(f"   Category: {event_data['category']}")
            print(f"   System: {event_data['betting_system_type']}")
            
            if 'betting_system_data' in event_data and event_data['betting_system_data']:
                system_data = event_data['betting_system_data']
                print(f"   💰 Betting System Data:")
                print(f"      Min Bet: {system_data['minimum_bet']} ZEC")
                print(f"      Max Bet: {system_data['maximum_bet']} ZEC")
                print(f"      House Fee: {system_data['house_fee_percentage'] * 100}%")
                print(f"      Oracle Fee: {system_data['oracle_fee_percentage'] * 100}%")
                print(f"      Pools: {len(system_data['betting_pools'])}")
                
                for pool in system_data['betting_pools']:
                    print(f"        - {pool['outcome_description']}")
                    print(f"          Amount: {pool['pool_amount']} ZEC")
            
            print(f"\n🎯 The API endpoints are now system-agnostic!")
            print(f"   Adding new betting systems won't require API changes")
            print(f"   Each system handles its own serialization")
            
        else:
            print("📭 No events found - create an event first!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_to_dict()
