#!/usr/bin/env python3
"""
Complete API testing script using FastAPI TestClient
"""

import sys
import json
from fastapi.testclient import TestClient

# Import our app
try:
    from ..app.main import app
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the backend directory")
    sys.exit(1)

def test_api_endpoints():
    """Test all our betting API endpoints"""
    print("🧪 Testing Betting API Endpoints...")
    print("=" * 50)
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Get all events
    print("\n📡 Testing GET /api/events")
    try:
        response = client.get("/api/events")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Found {len(events)} event(s)")
            
            if events:
                # Show first event details
                event = events[0]
                print(f"\n📋 Event Details:")
                print(f"   ID: {event['id']}")
                print(f"   Title: {event['title']}")
                print(f"   Category: {event['category']}")
                print(f"   Status: {event['status']}")
                print(f"   System: {event['betting_system_type']}")
                print(f"   Start Time: {event['event_start_time']}")
                
                # Show betting system data
                if event.get('betting_system_data'):
                    system_data = event['betting_system_data']
                    print(f"\n   💰 Betting System Data:")
                    print(f"      Min Bet: {system_data.get('minimum_bet')} ZEC")
                    print(f"      Max Bet: {system_data.get('maximum_bet')} ZEC")
                    print(f"      House Fee: {system_data.get('house_fee_percentage', 0) * 100}%")
                    print(f"      Oracle Fee: {system_data.get('oracle_fee_percentage', 0) * 100}%")
                    print(f"      Total Pool: {system_data.get('total_pool')} ZEC")
                    
                    pools = system_data.get('betting_pools', [])
                    print(f"      Betting Pools: {len(pools)}")
                    for i, pool in enumerate(pools, 1):
                        print(f"        {i}. {pool['outcome_description']}")
                        print(f"           Pool: {pool['pool_amount']} ZEC ({pool['bet_count']} bets)")
                
                # Test 2: Get single event
                event_id = event['id']
                print(f"\n📡 Testing GET /api/events/{event_id}")
                single_response = client.get(f"/api/events/{event_id}")
                print(f"Status Code: {single_response.status_code}")
                
                if single_response.status_code == 200:
                    single_event = single_response.json()
                    print(f"✅ Single event retrieved: {single_event['title']}")
                else:
                    print(f"❌ Single event request failed")
                    print(single_response.json())
                
                # Test 3: Filter by status
                print(f"\n📡 Testing GET /api/events?status=open")
                filter_response = client.get("/api/events?status=open")
                print(f"Status Code: {filter_response.status_code}")
                
                if filter_response.status_code == 200:
                    open_events = filter_response.json()
                    print(f"✅ Found {len(open_events)} open event(s)")
                
                # Test 4: Invalid event ID
                print(f"\n📡 Testing GET /api/events/999 (invalid ID)")
                invalid_response = client.get("/api/events/999")
                print(f"Status Code: {invalid_response.status_code}")
                
                if invalid_response.status_code == 404:
                    print(f"✅ Correctly returned 404 for invalid ID")
                else:
                    print(f"❌ Expected 404, got {invalid_response.status_code}")
                
            else:
                print("📭 No events found!")
                print("💡 Create some events first using: python test_create_event.py")
        
        else:
            print(f"❌ Events request failed: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    
    # Show next steps
    print(f"\n🚀 Next Steps:")
    print(f"   1. Start server: uvicorn app.main:app --reload --port 8000")
    print(f"   2. Visit: http://localhost:8000/api/events")
    print(f"   3. API docs: http://localhost:8000/docs")
    print(f"   4. Connect frontend to fetch from these endpoints")

if __name__ == "__main__":
    test_api_endpoints()
