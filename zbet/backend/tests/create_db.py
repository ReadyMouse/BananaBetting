#!/usr/bin/env python3
"""
Simple script to create database tables from our models
"""

from ..app.database import engine, Base
from ..app.models import User, SportEvent, PariMutuelEvent, PariMutuelPool, Bet, Payout

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Print table names to confirm
    print("\n📋 Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    create_tables()
