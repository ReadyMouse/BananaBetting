#!/usr/bin/env python3
"""
Test the betting API endpoints
"""

import requests
import subprocess
import time
import signal
import sys

def test_api():
    """Test our betting API endpoints"""
    try:
        # Test the events endpoint
        print("🧪 Testing API endpoints...")
        
        # Direct import test (without running server)
        from ..app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        print("📡 Testing GET /api/events")
        response = client.get("/api/events")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Found {len(events)} events")
            
            if events:
                event = events[0]
                print(f"📋 First Event:")
                print(f"   ID: {event['id']}")
                print(f"   Title: {event['title']}")
                print(f"   Category: {event['category']}")
                print(f"   Status: {event['status']}")
                print(f"   Betting System: {event['betting_system_type']}")
                
                if event.get('pari_mutuel_event'):
                    pari = event['pari_mutuel_event']
                    print(f"   💰 Pari-Mutuel Details:")
                    print(f"      Min Bet: {pari['minimum_bet']} ZEC")
                    print(f"      Max Bet: {pari['maximum_bet']} ZEC")
                    print(f"      Pools: {len(pari['betting_pools'])}")
                    
                    for pool in pari['betting_pools']:
                        print(f"        - {pool['outcome_description']}")
                        print(f"          Pool: {pool['pool_amount']} ZEC")
                
                # Test single event endpoint
                print(f"\n📡 Testing GET /api/events/{event['id']}")
                single_response = client.get(f"/api/events/{event['id']}")
                print(f"Status Code: {single_response.status_code}")
                
                if single_response.status_code == 200:
                    print("✅ Single event endpoint working!")
                else:
                    print("❌ Single event endpoint failed")
                    print(single_response.json())
            else:
                print("📭 No events found - create some events first!")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api()
