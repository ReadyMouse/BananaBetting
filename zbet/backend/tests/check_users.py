#!/usr/bin/env python3
"""
Check if users exist in the database after our changes
"""

from sqlalchemy.orm import sessionmaker
from ..app.database import engine
from ..app.models import User

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_users():
    """Check what users exist in the database"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        print(f"👥 Found {len(users)} user(s) in database:")
        
        if users:
            for user in users:
                print(f"📋 User ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Username: {user.username}")
                print(f"   Active: {user.is_active}")
                print(f"   Has Password: {'Yes' if user.hashed_password else 'No'}")
                print(f"   Zcash Address: {user.zcash_address}")
                print(f"   Balance: {user.balance}")
                print("-" * 40)
        else:
            print("📭 No users found!")
            print("💡 You may need to register a new account")
            print("💡 Or the database was reset when we recreated it")
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
