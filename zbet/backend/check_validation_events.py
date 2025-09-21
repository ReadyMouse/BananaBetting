#!/usr/bin/env python3
"""
Quick script to check what events are available for the test user to validate
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import User, SportEvent, Bet, EventStatus

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_validation_events():
    """Check what events the test user can validate"""
    db = SessionLocal()
    try:
        # Get test user
        test_user = db.query(User).filter(User.email == "test@gmail.com").first()
        if not test_user:
            print("❌ Test user not found!")
            return
        
        print(f"👤 Test user: {test_user.email} (ID: {test_user.id})")
        print("=" * 60)
        
        # Get all events
        all_events = db.query(SportEvent).all()
        print(f"📊 Total events in database: {len(all_events)}")
        
        # Check each event
        past_events = []
        future_events = []
        validation_events = []
        
        for event in all_events:
            # Check if test user has bet on this event
            user_bet = db.query(Bet).filter(
                Bet.user_id == test_user.id,
                Bet.sport_event_id == event.id
            ).first()
            
            has_bet = user_bet is not None
            is_past = "[PAST]" in event.title
            is_closed = event.status == EventStatus.CLOSED
            is_settled = event.status == EventStatus.SETTLED
            
            if is_past:
                past_events.append(event)
                if not has_bet and is_closed and not is_settled:
                    validation_events.append(event)
            else:
                future_events.append(event)
            
            status_icon = "⚖️" if is_settled else ("🔒" if is_closed else "🟢")
            bet_icon = "💰" if has_bet else "🚫"
            
            print(f"{status_icon} {bet_icon} {event.title[:60]}...")
            print(f"    Status: {event.status.value}, Test user bet: {'Yes' if has_bet else 'No'}")
            if is_past and not has_bet and is_closed and not is_settled:
                print(f"    ✨ AVAILABLE FOR VALIDATION")
            print()
        
        print("=" * 60)
        print("📋 Summary:")
        print(f"   📅 Past events: {len(past_events)}")
        print(f"   📅 Future events: {len(future_events)}")
        print(f"   🔍 Events available for validation: {len(validation_events)}")
        print()
        
        if validation_events:
            print("✅ Events you can validate:")
            for event in validation_events:
                print(f"   🎯 {event.title}")
        else:
            print("❌ No events available for validation")
            print("💡 Try running the seed script again to create validation events")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_validation_events()
